#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
author:chenzl
time : 2019-5-16
comment:先进先出方式，找天猫卡密成本
'''
from odps import ODPS
import re
import datetime
import string
import sys

reload(sys)
sys.setdefaultencoding('utf8')

# options.tunnel.use_instance_tunnel = True
# options.tunnel.limit_instance_tunnel = False  # 关闭limit限制，读取全部数据。

'''
获取昨日结余及当日导入作为当日的库存池
'''


def getCurStock(odps, cardStock, cardStockCol, part):
    table_name = "fuluappbigdata.dwd_stock_tmall_stocks"
    with o.get_table(table_name).open_reader(partition=part) as reader:
        print('当日库存期初总行数: %s' % reader.count)
        for record in reader:
            cardStockCol_key = record['global_key']
            cardStockCol_value = dict(record)
            cardStockCol[cardStockCol_key] = cardStockCol_value

            add_key = record['group_key']  ## 店铺商品唯一标识
            add_value = record['global_key']  ##每个入库记录的唯一标识
            if not add_key in cardStock:
                cardStock[add_key] = [add_value]
            else:
                cardStock[add_key].append(add_value)

    # 遍历排序
    for k, v in cardStock.items():
        v.sort()


'''
获取库存入库数据
'''


def loadDataBySql(o=None, sqlquery=None, key=None):
    if o == None:
        print('error:缺少odps连接对象!')
    elif sqlquery == None:
        print('error:缺少sql语句!')
    elif key == None:
        print('error:缺少关键字key!')
    else:
        pass

    rt = {}
    row = 0
    print('SqlQuery:%s' % re.sub(r"\s{2,}", " ", sqlquery))
    with o.execute_sql(sqlquery).open_reader(tunnel=True) as reader:
        print('###################################当日订单总行数: %s' % reader.count)
        for record in reader:
            row = row + 1
            rt[record[key]] = record
        return rt


'''
初始化odps
'''

'''
常量及变量
'''
# 表资源
cycdate = args['cycdate']
# cycdate = 20190605
part = 'pt=' + str(cycdate)

ZERO_STOCK = True if args['zerostock'].lower() == 'true' else False  # 是否允许最后一个库存为0后继续扣减,True 允许  False不允许
print(type(ZERO_STOCK))

# 入库明细
cardStock = {}
cardStockCol = {}
getCurStock(o, cardStock, cardStockCol, part)

# 销售订单
sqlquery = "SELECT  a.*,ROW_NUMBER() OVER(ORDER BY a.end_time ASC,a.order_id ASC ) AS rn,CONCAT(b.store_id,'-',a.goods_id) AS group_key,b.store_id \
FROM    (  \
            SELECT  order_id \
                    ,store_name \
                    ,cast(goods_id as string) as goods_id \
                    ,goods_name \
                    ,payment \
                    ,goods_num \
                    ,end_time \
            FROM    fuluappbigdata.dwd_trade_d_tmall_finish_order \
            WHERE   pt >= %s \
            AND     pt <= %s \
            AND     order_status = 'TRADE_FINISHED' \
            AND     TYPE = 'auto_delivery' \
            union all  \
            select orderid AS order_id,store_name,goods_id,goods_name AS goods_name,cast(amount as decimal) AS payment,cast(goods_num as bigint) as goods_num,cast(finish_time as datetime) AS end_time \
            FROM    fuluappbigdata.odps_accountflow_sku_pddorder_ch \
            WHERE   pt >= %s \
            AND     pt <= %s \
        ) AS a \
JOIN    ( \
            SELECT  DISTINCT store_id \
                    ,store_name \
            FROM    fuluappbigdata.dim_site2store_config \
        ) AS b \
ON      TRIM(a.store_name) = TRIM(b.store_name) " % (str(cycdate), str(cycdate), str(cycdate), str(cycdate))

saleOrder = loadDataBySql(o, sqlquery, 'rn')

salerecords = []
salerecord = []

## 数据输出
# part="pt='20190401'"
out = o.get_table('dwd_finance_d_tmall_sale')

if len(saleOrder) == 0:
    print("当日订单数是0")
    out.delete_partition(part, if_exists=True)
    out.create_partition(part, if_not_exists=True)  # 不存在的时候才创建
else:
    # 先进先出计算成本
    for i in range(len(saleOrder)):
        order = saleOrder[i + 1]
        print(
            "#######################遍历订单----订单号：{order_id},店铺：{store_name},商品id：{goods_id},商品名：{goods_name},购买商品数：{goods_num},用户支付总价：{payment},完结时间：{end_time}".format(
                **dict(order)))
        # 订单各属性赋值
        # 订单号
        orderid = order['order_id']
        # 店铺名
        storename = order['store_name']
        # 商品id
        goodsid = order['goods_id']
        # 商品名
        goodsname = order['goods_name']
        # 用户支付总价
        payment = order['payment']
        # 支付单价
        single_paymeng = order['payment'] / order['goods_num']
        # 购买商品数
        goodsnum = order['goods_num']
        # 完结时间
        endtime = order['end_time']
        # 仓库商品唯一标识
        groupkey = order['group_key']
        # 排序
        rn = order['rn']

        # 需要出库的总数量，会随着遍历入库记录而改变，初始默认是商品总数
        # 预计出库数
        need_out_num = order['goods_num']
        # 实际出库数
        # outnum = need_out_num

        # list，存储商品配置的主键
        cardstockvalue = cardStock[groupkey] if groupkey in cardStock else []
        cardstockvalue.sort()
        # 当前库存中的库存批次数
        cardstock_count = len(cardstockvalue)

        if cardstock_count == 0:
            # 无入库记录，找不到成本
            useComment = "无入库记录"
            print('%s： %s,继续遍历下一个订单......' % (orderid, useComment))
            salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment, None, None, None, None,
                          None,
                          None, None, None,
                          None, None,
                          None, None, None, None, None, useComment, need_out_num, payment]
            print(salerecord)
            salerecords.append(salerecord)
            continue
        else:
            # 有入库记录，那么遍历入库记录
            is_next_stock = False  # 标识是否是部分获取到。true 是，false 否

            # 遍历入库记录
            for sqe in range(len(cardstockvalue)):
                print("序号：%s   值：%s" % (sqe + 1, cardstockvalue[0]))
                cs = cardstockvalue[0]
                # 当前库存中总库存批次数
                cardstock_count = len(cardstockvalue)

                # 库存批次的详细信息，包含当前的结存，单价，供应商等信息
                cardStockrecord = cardStockCol[cs]
                print("sqe:%s   cs:%s  cardstock_count:%s cardstockvalue:%s cardStockrecord:%s" % (
                sqe, cs, cardstock_count, cardstockvalue, cardStockrecord['global_key']))
                print(
                    "################取入库记录----全局序号：{global_key},入库记录id：{input_id},入库时间：{create_time},现存量：{stock_num},库存单价：{price}".format(
                        **dict(cardStockrecord)))

                # 库存中的现存量
                stock_stocknum = cardStockrecord['stock_num']
                # 库存单价
                stock_price = cardStockrecord['price']
                stock_supplier_id = cardStockrecord['supplier_id']
                stock_supplier_name = cardStockrecord['supplier_name']
                stock_channel_id = cardStockrecord['channel_id']
                stock_channel_name = cardStockrecord['channel_name']
                stock_inventory_id = cardStockrecord['inventory_id']
                stock_inventory_name = cardStockrecord['inventory_name']
                stock_face_value = cardStockrecord['face_value']
                stock_busi_type = cardStockrecord['busi_type']
                stock_inventory_type = cardStockrecord['inventory_type']
                stock_goods_catetory_name = cardStockrecord['goods_catetory_name']
                stock_input_id = cardStockrecord['input_id']
                stock_create_time = cardStockrecord['create_time']

                # 结余，消耗卡密后，库存的剩余卡密数量
                balancenum = None

                # if endtime <= stock_create_time:
                #     # 消耗时间要早于入库，那么说明无卡可扣
                #     useComment = '[订单完结时间小于卡密入库时间]不允许卡密出库'
                #     print('找成本结果----%s： %s,退出遍历入库记录，继续遍历下一个订单......' % (orderid, useComment))
                #     salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment, None, None, None,
                #                   None, None, None, None,
                #                   None, None, None, None, None, None, None, None, useComment, need_out_num]
                #     print(salerecord)
                #     salerecords.append(salerecord)
                #     break
                # 取消出入库时间差异造成的不出库现象
                if False:
                    pass

                else:
                    # 消耗时间要晚于卡入库的时间
                    '''
                  消耗和库存数有三种不同的情况
                  '''
                    # 库存数量大于出库数
                    if stock_stocknum > need_out_num:
                        # 预计出库数
                        # need_out_num = outnum
                        # 实际出库数
                        outnum = need_out_num
                        # 结余
                        balancenum = stock_stocknum - outnum
                        # 出库价格
                        taxcost = stock_price * outnum
                        # 订单售价
                        taxamount = single_paymeng * outnum

                        useComment = '[库存数量大于出库数]找到部分卡密' if is_next_stock else '[库存数量大于出库数]找到全部卡密'
                        print('#######找成本结果----%s：出库数小于库存数， %s,插入记录，遍历下一个订单......' % (orderid, useComment))

                        salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment,
                                      stock_supplier_id,
                                      stock_supplier_name, stock_channel_id,
                                      stock_channel_name,
                                      stock_inventory_id,
                                      stock_inventory_name, stock_face_value,
                                      stock_busi_type, stock_inventory_type,
                                      stock_goods_catetory_name, taxcost, stock_input_id,
                                      stock_stocknum, outnum, balancenum,
                                      useComment, need_out_num, taxamount]
                        print(salerecord)
                        salerecords.append(salerecord)

                        # 修改库存的现存量
                        cardStockCol[cs]['stock_num'] = balancenum

                        # 从遍历库存中挑出，取下一条订单
                        break

                    # 库存数等于出库数
                    elif stock_stocknum == need_out_num:
                        # 预计出库数
                        # need_out_num = outnum
                        # 实际出库数
                        outnum = need_out_num
                        # 结余
                        balancenum = stock_stocknum - outnum
                        # 出库价格
                        taxcost = stock_price * outnum
                        # 订单售价
                        taxamount = single_paymeng * outnum

                        useComment = '[库存数等于出库数]找到部分卡密' if is_next_stock else '[库存数等于出库数]找到全部卡密'

                        print('#######找成本结果----%s：出库数等于库存数， %s,插入记录，遍历下一个订单......' % (orderid, useComment))

                        salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment,
                                      stock_supplier_id,
                                      stock_supplier_name, stock_channel_id,
                                      stock_channel_name,
                                      stock_inventory_id,
                                      stock_inventory_name, stock_face_value,
                                      stock_busi_type, stock_inventory_type,
                                      stock_goods_catetory_name, taxcost, stock_input_id,
                                      stock_stocknum, outnum, balancenum,
                                      useComment, need_out_num, taxamount]
                        print(salerecord)
                        salerecords.append(salerecord)

                        # 库存变为0，判断是否需要删除配置
                        if 1 == cardstock_count and ZERO_STOCK:
                            # if sqe + 1 == cardstock_count and ZERO_STOCK:
                            # 最后一个配置，允许最后一个配置库存为0
                            print('是最后一个配置，允许为0后继续扣除')
                            # 1-修改库存的现存量
                            cardStockCol[cs]['stock_num'] = balancenum

                        elif 1 == cardstock_count and not ZERO_STOCK:
                            # elif sqe + 1 == cardstock_count and not ZERO_STOCK:
                            # 最后一个配置，不允许最后一个配置库存为0
                            # 1-修改库存的现存量
                            cardStockCol[cs]['stock_num'] = balancenum
                            # # 2- 删除配置信息
                            # del cardStockCol[cs]
                            # # 3-删除索引
                            # del cardStock[groupkey][sqe]

                        else:
                            # 不是最后一个配置
                            # 1-修改库存的现存量
                            cardStockCol[cs]['stock_num'] = balancenum
                            # 2- 删除配置信息
                            del cardStockCol[cs]
                            # 3-删除索引
                            # del cardStock[groupkey][sqe]
                            del cardStock[groupkey][0]

                        break

                    # 库存数小于出库数
                    else:
                        # 库存变为0或者负数，判断是否需要删除配置
                        if 1 == cardstock_count and ZERO_STOCK:
                            # if sqe + 1 == cardstock_count and ZERO_STOCK:
                            # 最后一个配置，允许最后一个配置库存扣成负数
                            print('是最后一个配置，允许为0后继续扣除')
                            # 预计出库数
                            # need_out_num = outnum
                            # 实际出库数
                            outnum = need_out_num
                            # 结余
                            balancenum = stock_stocknum - outnum
                            # 出库价格
                            taxcost = stock_price * outnum
                            # 订单售价
                            taxamount = single_paymeng * outnum

                            useComment = '[库存数小于出库数,最后一个配置，允许最后一个配置库存扣成负数]找到部分卡密' if is_next_stock else '库存数小于出库数,最后一个配置，允许最后一个配置库存扣成负数,找到全部卡密'
                            print('#######找成本结果----%s %s' % (orderid, useComment))

                            # 1-修改库存的现存量
                            salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment,
                                          stock_supplier_id,
                                          stock_supplier_name, stock_channel_id,
                                          stock_channel_name,
                                          stock_inventory_id,
                                          stock_inventory_name, stock_face_value,
                                          stock_busi_type, stock_inventory_type,
                                          stock_goods_catetory_name, taxcost, stock_input_id,
                                          stock_stocknum, outnum, balancenum,
                                          useComment, need_out_num, taxamount]
                            print(salerecord)
                            salerecords.append(salerecord)

                            cardStockCol[cs]['stock_num'] = balancenum

                            break

                        elif 1 == cardstock_count and not ZERO_STOCK:
                            # elif sqe + 1 == cardstock_count and not ZERO_STOCK:
                            # 最后一个配置，不允许最后一个配置库存为0
                            # 预计出库数
                            # need_out_num = outnum
                            # 实际出库数
                            outnum = stock_stocknum
                            # 结余
                            balancenum = stock_stocknum - outnum
                            # 出库价格
                            taxcost = stock_price * outnum

                            # 预计出库数
                            # need_out_num = outnum
                            # 实际出库数
                            outnum = stock_stocknum if stock_stocknum > 0 else 0
                            # 结余
                            balancenum = stock_stocknum - outnum
                            # 出库价格
                            taxcost = stock_price * outnum
                            # 订单售价
                            taxamount = single_paymeng * need_out_num

                            if stock_stocknum > 0:
                                useComment = '[库存数小于出库数,最后一个配置，不允许最后一个配置库存为0]找到部分卡密'
                                print('#######找成本结果----%s %s' % (orderid, useComment))
                                salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment,
                                              stock_supplier_id,
                                              stock_supplier_name, stock_channel_id,
                                              stock_channel_name,
                                              stock_inventory_id,
                                              stock_inventory_name, stock_face_value,
                                              stock_busi_type, stock_inventory_type,
                                              stock_goods_catetory_name, taxcost, stock_input_id,
                                              stock_stocknum, outnum, balancenum,
                                              useComment, need_out_num, taxamount]
                            else:
                                useComment = '[库存数小于出库数,最后一个配置，不允许最后一个配置库存为0]库存为负不允许出库'
                                print('#######找成本结果----%s %s' % (orderid, useComment))
                                salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment,
                                              None,
                                              None, None,
                                              None,
                                              None,
                                              None, None,
                                              None, None,
                                              None, None, stock_input_id,
                                              stock_stocknum, outnum, balancenum,
                                              useComment, need_out_num, taxamount]
                            print(salerecord)
                            salerecords.append(salerecord)

                            # 1-修改库存的现存量
                            cardStockCol[cs]['stock_num'] = balancenum
                            # 2- 删除配置信息
                            # del cardStockCol[cs]
                            # 3-删除索引
                            # del cardStock[groupkey][sqe]

                            break

                        else:
                            # 不是最后一个配置
                            # 预计出库数
                            # need_out_num = outnum
                            # 实际出库数
                            outnum = stock_stocknum
                            # 结余
                            balancenum = stock_stocknum - outnum
                            # 出库价格
                            taxcost = stock_price * outnum
                            # 订单售价
                            taxamount = single_paymeng * outnum

                            useComment = '[库存数小于出库数,不是最后一个配置]找到部分卡密'
                            print('找成本结果----%s %s' % (orderid, useComment))

                            salerecord = [orderid, storename, goodsid, goodsname, goodsnum, endtime, payment,
                                          stock_supplier_id,
                                          stock_supplier_name, stock_channel_id,
                                          stock_channel_name,
                                          stock_inventory_id,
                                          stock_inventory_name, stock_face_value,
                                          stock_busi_type, stock_inventory_type,
                                          stock_goods_catetory_name, taxcost, stock_input_id,
                                          stock_stocknum, outnum, balancenum,
                                          useComment, need_out_num, taxamount]
                            print(salerecord)
                            salerecords.append(salerecord)

                            # 1-修改库存的现存量
                            cardStockCol[cs]['stock_num'] = balancenum
                            # 2- 删除配置信息
                            del cardStockCol[cs]
                            # 3-删除索引
                            del cardStock[groupkey][0]
                            # del cardStock[groupkey][sqe]

                            # 预计下次出库数
                            need_out_num = need_out_num - outnum
                            is_next_stock = True  # 标识是否是部分获取到。true 是，false 否

                            # continue

# 删除分区
out.delete_partition(part, if_exists=True)
with out.open_writer(partition=part, create_partition=True) as writer:
    writer.write(salerecords)
    writer.close()
