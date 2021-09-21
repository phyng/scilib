# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from .base import call, call_batch, call_from_file


def start_with_cd(working_dir):
    return call_batch(
        call('clear all'),
        call('macro drop _all'),
        call(f'cd "{working_dir}"'),
        call('pwd'),
    )


def xls2dta(xlsx_file, dta_file):
    return call_batch(
        call(f'capture erase "{dta_file}"'),
        call(f'xls2dta:import excel using "{xlsx_file}", firstrow'),
        call(f'use "{dta_file}"')
    )


def summary(var_list, row_list='变量名称 均值 标准差 最大值 方差 最小值', word_file='mytable.docx'):
    return call_from_file(
        '_summary.do',
        REPLACE_VAR_LIST=var_list,
        REPLACE_ROW_LIST=row_list,
        REPLACE_WORE_FILE=word_file,
    )


def reg(var_list):
    return call_batch(
        call('reg', var_list),
        call('estat vif'),
    )


def nbreg(var_list, word_file='mytable.docx'):
    return call_batch(
        call('nbreg', var_list, ',r'),
        call('est store m1'),
        call("""
            reg2docx m1 using REPLACE_WORE_FILE,         ///
            b(%5.3f) t(%5.3f) scalars(N p(%9.3f))   ///
            title("表1: 负二项回归输出") mtitles("模型") append
        """.replace('REPLACE_WORE_FILE', word_file)),
        call('reg', var_list),
        call('estat imtest, white'),
        call('reg', var_list, ', vce(robust)'),
        call('est store m2'),
        call("""
            reg2docx m2 using REPLACE_WORE_FILE,         ///
            b(%5.3f) se(%9.2f) scalars(N p(%9.3f))   ///
            title("表2: 线性回归模型") mtitles("模型") append
        """.replace('REPLACE_WORE_FILE', word_file)),
    )
