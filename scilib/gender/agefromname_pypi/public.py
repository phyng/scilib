# coding: utf-8

from agefromname import AgeFromName


def batch_classify(names):
    first_names = [i.split()[0].lower() for i in names]

    age_from_name = AgeFromName()
    df_all_result = age_from_name.get_all_name_male_prob()
    result_map = {}
    for index, row in df_all_result.iterrows():
        if row['prob'] > 0.5:
            result_map[str(index)] = 'male'
        elif row['prob'] > 0 and row['prob'] < 0.5:
            result_map[str(index)] = 'female'
        else:
            result_map[str(index)] = 'unknown'

    results = []
    for first_name in first_names:
        if first_name in result_map:
            results.append(result_map[first_name])
        else:
            results.append('unknown')
    return results
