#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   miscellaneous.py
@Time    :   2022/12/30 14:32:29
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022, Thomas Aussaguès
@Desc    :   None
'''

def bool_to_colored_str(boolean : bool) -> str :

    if boolean :
        return '\x1b[0;37;42m' + str(boolean) + '\x1b[0m'

    else :
        return '\x1b[0;37;41m' + str(boolean) + '\x1b[0m'

