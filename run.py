"""
Program to convert the csv raw data of salary information to a json for uploading to mongoDB
"""
import pandas as pd
import numpy as np
import re
def main():

    # Variables
    default_variable_bonus_value = 0
    default_year = 2021

    # Read the input file
    df = pd.read_csv('input.csv')

    # Remove existing human readable headers to concise one's for reducing json payload
    mapping = {df.columns[0]: 'timestamp', df.columns[1]:'location', df.columns[2]:'title', df.columns[3]:'base_salary', df.columns[4]:'stock_options', df.columns[5]:'bonus', df.columns[6]:'cash_equity', df.columns[7]:'empty', df.columns[8]:'experience', df.columns[9]:'highest_education', df.columns[10]:'bootcamp', df.columns[11]:'year', df.columns[12]:'industry', df.columns[13]:'other_industry', df.columns[14]:'faang_mmanga', df.columns[15]:'company_size'}
    df = df.rename(columns=mapping)

    # Drop the empty column H
    df.drop('empty', axis=1, inplace=True)

    # Remove $ symbol from the base_salary cell
    df['base_salary'] = df['base_salary'].map(lambda x: int(x.lstrip('$').replace(r'.000','').replace(',','').replace('TC','')))

    # Make the timestamp pretty
    df['timestamp'] = df['timestamp'].map(lambda x: x.replace('/','-'))

    # Some bonus are mentioned in %
    # Convert the % bonus to the actual value based on the base salary
    
    # One entry had varible mentioned in the cell, changing it to 0 : BUG - WIP
    df['final_bonus'] = df['bonus'].map(lambda x: x.replace('variable',str(default_variable_bonus_value)))
    
    # Removing all texts from the bonus field, Bonus, and % of Bonus etc
    df['final_bonus'] = df['final_bonus'].map(lambda x: re.sub(r'[a-zA-Z,\s]','',x))

    # If the cell contains % calculate the actual bonus amount
    pct = df['final_bonus'].str.contains('%')
    df.loc[pct, 'final_bonus'] = df.loc[pct, 'final_bonus'].str.rstrip('%').astype('float') / 100.0 * (df.loc[pct, 'base_salary'])
    
    # Copy the final bonus into the original cell
    df['bonus'] = df['final_bonus']

    # Format year
    df['year'] = df['year'].astype('str')
    df['year'] = df['year'].map(lambda x: x.replace('\s',default_year))
    df['year'] = df['year'].astype(str).apply(lambda x: x.replace('.0', ''))

    # Format Company Size 
    # Bug : CSV download sometimes is considering company size of 11-50 as Nov-50
    df['company_size'] = df['company_size'].apply(lambda x: x.replace('Nov', '11'))
    
    # Remove the temp final_bonus column
    df.drop('final_bonus', axis=1, inplace=True)

    # Convert to JSON
    df.to_json ('output.json', orient='records')

if __name__ == "__main__":
    main()