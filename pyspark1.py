# -*-coding:utf-8-*-
__author__ = 'Administrator'

from pyspark.sql
import SparkSession
import networkx as nx
from pyspark.sql.types
import StringType, StructField, StructType, DoubleType
from networkx.algorithms.flow import maximum_flow
from networkx.exception import NetworkXError
import pyspark.sql.functions as F
from pyspark.sql import window
import itertools import sys import time


spark = SparkSession.builder.appName('maxflow')getOrCreate()

sc = spark.sparkcContext
sc. setLogLevel('ERROR')


limit = 50000
database = 'zchen'
trans_table = 'tia.input'  #输入的边集合（交易流水）
constable = 'tia_result'  #输入社区划分的结果（节点编号，交易圈编号）
output_table = 'tiaJXow'   #输出的表名
batch = '20210529' #创建hive表

def graph.create(args):
    G = nx.DiGraph()  #建有向图
    G.add_edges_from(args)
    return G

# 建spark的表
#spark.sql('create table ai.zchen_How(src string, dst string, flow double, comid stri


def data_process(rdd, directed):
    schema = StructType([])
