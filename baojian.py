import os
import shutil
import xlrd
import xml.dom.minidom as xdm
import random
import hashlib
import datetime
import lxml.etree as et
from io import StringIO
from ftplib import FTP
import time
import json


setting = json.load(open('setting.json', 'r', encoding='utf-8'), encoding='utf-8')
_local_path = setting['local_path']
_xls_backup = setting['xls_backup']
_xml_backup = setting['xml_backup']
# 测试FTP服务器
# _ip = '192.168.4.196'
# _uname = 'renji'
# _pwd = 'renji'
# _port = 21
# 正式FTP服务器
_ip = '122.114.201.11'
_uname = 'vipomsZB'
_pwd = 'vipomsBS'
_port = 211


def md5_num():
    md5 = hashlib.md5()
    ran = repr(random.uniform(1, 100)).encode('utf-8')
    md5.update(ran)
    return md5.hexdigest().upper()


def get_value(row, column, sheet):
    if sheet.cell_type(row, column) == 1:   # type 1 is text
        return sheet.cell_value(row, column)
    else:
        return str(int(sheet.cell_value(row, column)))


def get_price(row, column, sheet):
    if sheet.cell_type(row, column) == 2:  # type 2 is number(float)
        return str(round(sheet.cell_value(row, column), 3))
    else:
        return sheet.cell_value(row, column)


class Transfer(object):
    def __init__(self):
        self.ftp = None

    def setParams(self, ip=_ip, uname=_uname, pwd=_pwd, port=_port, timeout=60):
        self.ip = ip
        self.uname = uname
        self.pwd = pwd
        self.port = port
        self.timeout = timeout

    def initEnv(self):
        if self.ftp is None:
            self.ftp = FTP()
            print('连接FTP服务器中……')
            self.ftp.connect(self.ip, self.port, self.timeout)
            self.ftp.login(self.uname, self.pwd)

    def clearEnv(self):
        if self.ftp:
            self.ftp.close()
            print("与FTP服务器断开\n=====================")

    def upload(self, file):
        self.ftp.storbinary('STOR ' + os.path.basename(file), open((_local_path +file), 'rb'))
        print('xml文件上传成功')


def get_excels(local_path):
    return [x for x in os.listdir(local_path) if os.path.splitext(x)[1] == '.xls']


def create_xml(files):
    for xls_file in files:
        file = xlrd.open_workbook(_local_path + xls_file)
        sheet1 = file.sheet_by_index(0)
        sheet2 = file.sheet_by_index(1)

        doc = xdm.Document()
        root = doc.createElement('ENT801Message')
        root.setAttribute('xmlns', 'http://www.chinaport.gov.cn/ENT',)
        root.setAttribute('sendCode', 'sendcode')
        root.setAttribute('reciptCode', 'reciptcode')
        doc.appendChild(root)

        application = root.appendChild(doc.createElement('Application'))
        applicationHead = application.appendChild(doc.createElement('ApplicationHead'))

        nodeID = doc.createElement('ID')
        nodeID.appendChild(doc.createTextNode(md5_num()))
        nodeSBD_NO = doc.createElement('SBD_NO')
        nodeSBD_NO.appendChild(doc.createTextNode('4109002' + str(sheet2.cell_value(5, 7))
                                                  + datetime.datetime.now().strftime('%Y%m%d%U%f')))
        nodeSBQYBA_NO = doc.createElement('SBQYBA_NO')
        nodeSBQYBA_NO.appendChild(doc.createTextNode(get_value(5, 7, sheet2)))
        nodeWB_CODE = doc.createElement('WB_CODE')
        nodeWB_CODE.appendChild(doc.createTextNode(get_value(6, 7, sheet2)))
        nodeIE_FLAG = doc.createElement('IE_FLAG')
        nodeIE_FLAG.appendChild(doc.createTextNode('I'))
        nodeMODIFY_MARK = doc.createElement('MODIFY_MARK')
        nodeMODIFY_MARK.appendChild(doc.createTextNode('1'))
        nodeDSQY_CODE = doc.createElement('DSQY_CODE')
        nodeDSQY_CODE.appendChild(doc.createTextNode(sheet2.cell_value(9, 7)))
        nodeDSQY_NAME = doc.createElement('DSQY_NAME')
        nodeDSQY_NAME.appendChild(doc.createTextNode(sheet2.cell_value(10, 7)))
        nodeWLQY_CODE = doc.createElement('WLQY_CODE')
        nodeWLQY_CODE.appendChild(doc.createTextNode(sheet2.cell_value(11, 7)))
        nodeWLQY_NAME = doc.createElement('WLQY_NAME')
        nodeWLQY_NAME.appendChild(doc.createTextNode(sheet2.cell_value(12, 7)))
        nodeSB_DATE = doc.createElement('SB_DATE')
        nodeSB_DATE.appendChild(doc.createTextNode(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        nodeLXR = doc.createElement('LXR')
        nodeLXR.appendChild(doc.createTextNode(sheet2.cell_value(14, 7)))
        nodeLXR_PHONE = doc.createElement('LXR_PHONE')
        nodeLXR_PHONE.appendChild(doc.createTextNode(sheet2.cell_value(15, 7)))
        nodeREC_NAME_CN = doc.createElement('REC_NAME_CN')
        nodeREC_NAME_CN.appendChild(doc.createTextNode(sheet2.cell_value(16, 7)))
        nodeREC_NAME_EN = doc.createElement('REC_NAME_EN')
        nodeREC_NAME_EN.appendChild(doc.createTextNode(sheet2.cell_value(17, 7)))
        nodeSEND_NAME_CN = doc.createElement('SEND_NAME_CN')
        nodeSEND_NAME_CN.appendChild(doc.createTextNode(sheet2.cell_value(18, 7)))
        nodeSEND_NAME_EN = doc.createElement('SEND_NAME_EN')
        nodeSEND_NAME_EN.appendChild(doc.createTextNode(sheet2.cell_value(19, 7)))
        nodeLOCAL_JYJYJG = doc.createElement('LOCAL_JYJYJG')
        nodeLOCAL_JYJYJG.appendChild(doc.createTextNode(sheet2.cell_value(20, 7)))
        nodeQYKA_CODE = doc.createElement('QYKA_CODE')
        nodeQYKA_CODE.appendChild(doc.createTextNode(sheet2.cell_value(21, 7)))
        nodeQYKA = doc.createElement('QYKA')
        nodeQYKA.appendChild(doc.createTextNode(sheet2.cell_value(22, 7)))
        nodeRJKA_CODE = doc.createElement('RJKA_CODE')
        nodeRJKA_CODE.appendChild(doc.createTextNode(sheet2.cell_value(23, 7)))
        nodeRJKA = doc.createElement('RJKA')
        nodeRJKA.appendChild(doc.createTextNode(sheet2.cell_value(24, 7)))
        nodeTRANS_CODE = doc.createElement('TRANS_CODE')
        nodeTRANS_CODE.appendChild(doc.createTextNode(sheet2.cell_value(25, 7)))
        nodeTRANS_NAME = doc.createElement('TRANS_NAME')
        nodeTRANS_NAME.appendChild(doc.createTextNode(sheet2.cell_value(26, 7)))
        nodeTRANS_NO = doc.createElement('TRANS_NO')
        nodeTRANS_NO.appendChild(doc.createTextNode(sheet2.cell_value(27, 7)))
        nodeTRADE_COUNTRY_CODE = doc.createElement('TRADE_COUNTRY_CODE')
        nodeTRADE_COUNTRY_CODE.appendChild(doc.createTextNode(sheet2.cell_value(28, 7)))
        nodeTRADE_COUNTRY = doc.createElement('TRADE_COUNTRY')
        nodeTRADE_COUNTRY.appendChild(doc.createTextNode(sheet2.cell_value(29, 7)))
        nodeQY_COUNTRY_CODE = doc.createElement('QY_COUNTRY_CODE')
        nodeQY_COUNTRY_CODE.appendChild(doc.createTextNode(sheet2.cell_value(30, 7)))
        nodeQY_COUNTRY = doc.createElement('QY_COUNTRY')
        nodeQY_COUNTRY.appendChild(doc.createTextNode(sheet2.cell_value(31, 7)))
        nodeARR_DATE = doc.createElement('ARR_DATE')
        arr_date = sheet2.cell_value(33, 7)
        strp = datetime.datetime.strptime(arr_date, '%Y/%m/%d')
        nodeARR_DATE.appendChild(doc.createTextNode(strp.strftime('%Y-%m-%d')))
        nodePACK_TYPE = doc.createElement('PACK_TYPE')
        nodePACK_TYPE.appendChild(doc.createTextNode(sheet2.cell_value(37, 7)))
        nodePACK_TYPE_NAME = doc.createElement('PACK_TYPE_NAME')
        nodePACK_TYPE_NAME.appendChild(doc.createTextNode(sheet2.cell_value(38, 7)))
        nodeGROSS_WEIGHT = doc.createElement('GROSS_WEIGHT')
        nodeGROSS_WEIGHT.appendChild(doc.createTextNode(sheet2.cell_value(40, 7)))
        nodeWEIGHT_TYPE = doc.createElement('WEIGHT_TYPE')
        nodeWEIGHT_TYPE.appendChild(doc.createTextNode(sheet2.cell_value(41, 7)))
        nodeGOODS_NUM = doc.createElement('GOODS_NUM')
        nodeGOODS_NUM.appendChild(doc.createTextNode(get_value(43, 7, sheet2)))
        nodeNUM_TYPE = doc.createElement('NUM_TYPE')
        nodeNUM_TYPE.appendChild(doc.createTextNode(sheet2.cell_value(44, 7)))
        nodeFJ_FLAG = doc.createElement('FJ_FLAG')
        nodeFJ_FLAG.appendChild(doc.createTextNode('N' if sheet2.cell_value(45, 7) == '否' else 'Y'))
        nodeZWX_FLAG = doc.createElement('ZWX_FLAG')
        nodeZWX_FLAG.appendChild(doc.createTextNode('N' if str(sheet2.cell_value(46, 7)) == '否' else 'Y'))
        for line in range(sheet1.nrows-1):
            line += 1
            nodeItemID = doc.createElement('ID')
            nodeItemID.appendChild(doc.createTextNode(sheet1.cell_value(line, 0)))
            nodeITEM_NO = doc.createElement('ITEM_NO')
            nodeITEM_NO.appendChild(doc.createTextNode(sheet1.cell_value(line, 1)))
            nodeGOODS_NO = doc.createElement('GOODS_NO')
            nodeGOODS_NO.appendChild(doc.createTextNode(sheet1.cell_value(line, 2)))
            nodeSHEL_GOODS_NAME = doc.createElement('SHEL_GOODS_NAME')
            nodeSHEL_GOODS_NAME.appendChild(doc.createTextNode(sheet1.cell_value(line, 3)))
            nodeHS_CODE = doc.createElement('HS_CODE')
            nodeHS_CODE.appendChild(doc.createTextNode(get_value(line, 4, sheet1)))
            nodeSB_GOODS_NAME = doc.createElement('SB_GOODS_NAME')
            nodeSB_GOODS_NAME.appendChild(doc.createTextNode(sheet1.cell_value(line, 5)))
            nodeGGXH = doc.createElement('GGXH')
            nodeGGXH.appendChild(doc.createTextNode(sheet1.cell_value(line, 6)))
            nodeCJ_PRICE = doc.createElement('CJ_PRICE')
            nodeCJ_PRICE.appendChild(doc.createTextNode(get_price(line, 7, sheet1)))
            nodeCURRENCY_CODE = doc.createElement('CURRENCY_CODE')
            nodeCURRENCY_CODE.appendChild(doc.createTextNode(sheet1.cell_value(line, 8)))
            nodeCURRENCY = doc.createElement('CURRENCY')
            nodeCURRENCY.appendChild(doc.createTextNode(sheet1.cell_value(line, 9)))
            nodeQUANTITY = doc.createElement('QUANTITY')
            nodeQUANTITY.appendChild(doc.createTextNode(get_value(line, 10, sheet1)))
            nodePRICETOTAL = doc.createElement('PRICETOTAL')
            nodePRICETOTAL.appendChild(doc.createTextNode(get_price(line, 11, sheet1)))
            nodeUNIT_CODE = doc.createElement('UNIT_CODE')
            nodeUNIT_CODE.appendChild(doc.createTextNode(get_value(line, 12, sheet1)))
            nodeUNIT = doc.createElement('UNIT')
            nodeUNIT.appendChild(doc.createTextNode(sheet1.cell_value(line, 13)))
            nodeItemGROSS_WEIGHT = doc.createElement('GROSS_WEIGHT')
            nodeItemGROSS_WEIGHT.appendChild(doc.createTextNode(str(sheet1.cell_value(line, 14))))
            nodeWEIGHT_UTIL = doc.createElement('WEIGHT_UTIL')
            nodeWEIGHT_UTIL.appendChild(doc.createTextNode(sheet1.cell_value(line, 15)))
            nodeItemFJ_FLAG = doc.createElement('FJ_FLAG')
            nodeItemFJ_FLAG.appendChild(doc.createTextNode(sheet1.cell_value(line, 16)))
            nodeItemZWX_FLAG = doc.createElement('ZWX_FLAG')
            nodeItemZWX_FLAG.appendChild(doc.createTextNode('N'))
            nodeORIGIN_COUNTRY_CODE = doc.createElement('ORIGIN_COUNTRY_CODE')
            nodeORIGIN_COUNTRY_CODE.appendChild(doc.createTextNode(sheet1.cell_value(line, 17)))
            nodeORIGIN_COUNTRY = doc.createElement('ORIGIN_COUNTRY')
            nodeORIGIN_COUNTRY.appendChild(doc.createTextNode(sheet1.cell_value(line, 18)))
            nodeItemPACK_TYPE = doc.createElement('PACK_TYPE')
            nodeItemPACK_TYPE.appendChild(doc.createTextNode(sheet1.cell_value(line, 19)))
            nodePACK_NUM = doc.createElement('PACK_NUM')
            nodePACK_NUM.appendChild(doc.createTextNode(sheet1.cell_value(line, 20)))
            nodeBD_VOYAGE_NO = doc.createElement('BD_VOYAGE_NO')
            nodeBD_VOYAGE_NO.appendChild(doc.createTextNode(sheet2.cell_value(6, 7)))

            applicationList = application.appendChild(doc.createElement('ApplicationList'))
            applicationList.appendChild(nodeItemID)
            applicationList.appendChild(nodeITEM_NO)
            applicationList.appendChild(nodeGOODS_NO)
            applicationList.appendChild(nodeSHEL_GOODS_NAME)
            applicationList.appendChild(nodeHS_CODE)
            applicationList.appendChild(nodeSB_GOODS_NAME)
            applicationList.appendChild(nodeGGXH)
            applicationList.appendChild(nodeCJ_PRICE)
            applicationList.appendChild(nodeCURRENCY_CODE)
            applicationList.appendChild(nodeCURRENCY)
            applicationList.appendChild(nodeQUANTITY)
            applicationList.appendChild(nodePRICETOTAL)
            applicationList.appendChild(nodeUNIT_CODE)
            applicationList.appendChild(nodeUNIT)
            applicationList.appendChild(nodeItemGROSS_WEIGHT)
            applicationList.appendChild(nodeWEIGHT_UTIL)
            applicationList.appendChild(nodeItemFJ_FLAG)
            applicationList.appendChild(nodeItemZWX_FLAG)
            applicationList.appendChild(nodeORIGIN_COUNTRY_CODE)
            applicationList.appendChild(nodeORIGIN_COUNTRY)
            applicationList.appendChild(nodeItemPACK_TYPE)
            applicationList.appendChild(nodePACK_NUM)
            applicationList.appendChild(nodeBD_VOYAGE_NO)

        applicationHead.appendChild(nodeID)
        applicationHead.appendChild(nodeSBD_NO)
        applicationHead.appendChild(nodeSBQYBA_NO)
        applicationHead.appendChild(nodeWB_CODE)
        applicationHead.appendChild(nodeIE_FLAG)
        applicationHead.appendChild(nodeMODIFY_MARK)
        applicationHead.appendChild(nodeDSQY_CODE)
        applicationHead.appendChild(nodeDSQY_NAME)
        applicationHead.appendChild(nodeWLQY_CODE)
        applicationHead.appendChild(nodeWLQY_NAME)
        applicationHead.appendChild(nodeSB_DATE)
        applicationHead.appendChild(nodeLXR)
        applicationHead.appendChild(nodeLXR_PHONE)
        applicationHead.appendChild(nodeREC_NAME_CN)
        applicationHead.appendChild(nodeREC_NAME_EN)
        applicationHead.appendChild(nodeSEND_NAME_CN)
        applicationHead.appendChild(nodeSEND_NAME_EN)
        applicationHead.appendChild(nodeLOCAL_JYJYJG)
        applicationHead.appendChild(nodeQYKA_CODE)
        applicationHead.appendChild(nodeQYKA)
        applicationHead.appendChild(nodeRJKA_CODE)
        applicationHead.appendChild(nodeRJKA)
        applicationHead.appendChild(nodeTRANS_CODE)
        applicationHead.appendChild(nodeTRANS_NAME)
        applicationHead.appendChild(nodeTRANS_NO)
        applicationHead.appendChild(nodeTRADE_COUNTRY_CODE)
        applicationHead.appendChild(nodeTRADE_COUNTRY)
        applicationHead.appendChild(nodeQY_COUNTRY_CODE)
        applicationHead.appendChild(nodeQY_COUNTRY)
        applicationHead.appendChild(nodeARR_DATE)
        applicationHead.appendChild(nodePACK_TYPE)
        applicationHead.appendChild(nodePACK_TYPE_NAME)
        applicationHead.appendChild(nodeGROSS_WEIGHT)
        applicationHead.appendChild(nodeWEIGHT_TYPE)
        applicationHead.appendChild(nodeGOODS_NUM)
        applicationHead.appendChild(nodeNUM_TYPE)
        applicationHead.appendChild(nodeFJ_FLAG)
        applicationHead.appendChild(nodeZWX_FLAG)

        xmlFileName = str(datetime.datetime.now().strftime('%Y%m%d%U%f')) + '.xml'
        fp = open(_local_path + xmlFileName, 'w', encoding='utf-8')
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
        print('xml文件生成成功！')
        fp.close()

        if xmlFileName:
            xsd_file = StringIO(open('ENT801.xsd', 'r', encoding='utf-8').read())
            xmlschema_doc = et.parse(xsd_file)
            xmlschema = et.XMLSchema(xmlschema_doc)
            xml_file = open(_local_path + xmlFileName, 'r', encoding='utf-8').read()
            valid_str = StringIO(xml_file[39:])
            xml = et.parse(valid_str)

            if xmlschema.validate(xml) is True:
                print('xml文件验证通过')
                transfer = Transfer()
                transfer.setParams()
                transfer.initEnv()
                transfer.upload(xmlFileName)
                print('《' + xls_file + '》 处理完成！')
                shutil.move(_local_path + xmlFileName, _xml_backup)
                try:
                    shutil.move(_local_path + xls_file, _xls_backup)
                except shutil.Error as e:
                    print('*注意*：此Excel已在备份文件夹中存在，移动至备份文件夹失败！')

                transfer.clearEnv()
            else:
                print('xml文件验证失败，原因如下：')
                print(xmlschema.error_log)

excels = get_excels(_local_path)
if excels:
    create_xml(excels)
else:
    print('未发现报检单excel文件')
for x in range(10000):
    print('请按CRTL + C 退出程序')
    time.sleep(3)
# pyinstaller -F -i C:\Users\Administrator\Downloads\panda_128px_1179072_easyicon.net.ico baojian.py
