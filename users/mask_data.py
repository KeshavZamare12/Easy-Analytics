import pandas as pd

def mask_data_method(df, selected_cols, pattern):
    for col in selected_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda item: mask_item(item, pattern))
    return df

def mask_item(item, pattern):
    if len(item) >= len(pattern):
        masked_item = list(item)  
        start_index = pattern.find('x')
        end_index = pattern.rfind('x')
        end_index = start_index + (len(item) - end_index - 1)
        for i in range(len(item)):
            if i >= start_index and i <= end_index:
                masked_item[i] = 'x'  

        return ''.join(masked_item)  
    else:
        return item