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
            title("表: 负二项回归输出") mtitles("模型") append
        """.replace('REPLACE_WORE_FILE', word_file)),
        call('reg', var_list),
        call('estat imtest, white'),
        call('reg', var_list, ', vce(robust)'),
        call('est store m2'),
        call("""
            reg2docx m2 using REPLACE_WORE_FILE,         ///
            b(%5.3f) se(%9.2f) scalars(N p(%9.3f))   ///
            title("表: 线性回归模型") mtitles("模型") append
        """.replace('REPLACE_WORE_FILE', word_file)),
    )


def psm(var_treat, var_deps, var_result, word_file='mytable.docx'):

    def graph(suffix):
        return [
            call(f'* 均衡性检验 {suffix}'),
            call(f'* PUT_TO_EXCEL_START:{suffix}_pstest'),
            call('pstest $v2, both graph'),
            call(f'* PUT_TO_EXCEL_END:{suffix}_pstest'),
            call(f'graph export pstest_{suffix}.eps, replace'),

            call(f'* 共同取值范围 {suffix}'),
            call('psgraph'),
            call(f'graph export psgraph_{suffix}.eps, replace'),
        ]

    return call_batch(
        call('set seed 20211209'),
        call('gen u=runiform()'),
        call('sort u'),
        call(f'local v1 "{var_treat}"'),
        call(f'local v2 "{var_deps}"'),
        call(""" global x "`v1' `v2'" """),

        call('* 一元回归'),
        call(f'reg {var_result} {var_treat}, r'),
        call('est store pm1'),

        call('* 多元回归'),
        call(f'reg {var_result} $x, r'),
        call('est store pm2'),
        call("""
            reg2docx pm1 pm2 using REPLACE_WORE_FILE,         ///
            b(%5.3f) se(%9.2f) scalars(N p(%9.3f))   ///
            title("表: 一元回归/多元回归") mtitles("一元回归" "多元回归") append
        """.replace('REPLACE_WORE_FILE', word_file)),

        call('* 1:1 匹配，默认有放回'),
        call(f'psmatch2 $x, out({var_result}) neighbor(1) ate ties logit common'),
        *graph('1_1'),

        call('* 最近邻匹配，k=4'),
        call(f'psmatch2 $x, out({var_result}) n(4) ate ties logit common'),
        *graph('1_4'),

        call('* 计算倾向得分'),
        call('sum _pscore'),
        call('dis 0.25 * r(sd)'),

        call('* 半径匹配'),
        call(f'psmatch2  $x, out({var_result}) n(4) cal(0.01) ate ties logit common'),
        *graph('r'),

        call('* 核匹配，使用默认的核函数和带宽'),
        call(f'psmatch2 $x, out({var_result})  kernel ate ties logit common'),
        *graph('k'),

        call('* 核密度函数图'),
        call(
            'twoway(kdensity _ps if _treat==1,legend(label(1 "Treat")))(kdensity _ps '
            'if _treat==0, legend(label(2 "Control"))),xtitle(Pscore) title("Before Matching")'
        ),
        call('graph export before.eps, replace'),

        call(
            'twoway(kdensity _ps if _treat==1,legend(label(1 "Treat")))(kdensity _ps '
            'if (_weight!=1&_weight!=.), legend(label(2 "Control"))), xtitle(Pscore) title("After Matching")'
        ),
        call('graph export after.eps, replace'),
    )
