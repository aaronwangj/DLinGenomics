"""
    This script file contains all the functions that deal anything with parsing anything.
"""
import pandas as pd
import numpy as np
from src.util import exists, get_files_recursively
import os
from sklearn.model_selection import train_test_split

def create_empty_dataframe():
    return pd.DataFrame({ 'GeneID' : pd.Series([], dtype=np.int32), 
                          'BinID' : pd.Series([], dtype=np.int32), 
                          'H3K27me3': pd.Series([], dtype=np.float32),
                          'H3K36me3': pd.Series([], dtype=np.float32), 
                          'H3K4me1': pd.Series([], dtype=np.float32), 
                          'H3K4me3': pd.Series([], dtype=np.float32),
                          'H3K9me3': pd.Series([], dtype=np.float32),
                          'Expression': pd.Series([], dtype=np.float32)
                        }
                    )

def parse_cell_csv_file(path):
    if exists(path):
        dataframe = pd.read_csv(path, 
                names=['GeneID', 'BinID', 'H3K27me3', 'H3K36me3', 'H3K4me1', 'H3K4me3', 'H3K9me3', 'Expression'],
                dtype={ 'GeneID' : np.int32, 
                        'BinID' : np.int32, 
                        'H3K27me3': np.float32,
                        'H3K36me3': np.float32, 
                        'H3K4me1': np.float32, 
                        'H3K4me3': np.float32,
                        'H3K9me3': np.float32,
                        'Expression': np.float32
                    }
            )
        return dataframe
    else:
        return create_empty_dataframe()
        


def parse_all_cell_files(path):
    all_files = get_files_recursively(path)
    all_files = list(filter(lambda x: '.csv' in x, all_files))
    
    all_cell_genes = create_empty_dataframe()

    for cell_file in all_files:
        all_cell_genes = pd.concat([all_cell_genes, parse_cell_csv_file(cell_file)]).drop_duplicates()


    gene_ids = np.sort(all_cell_genes['GeneID'].drop_duplicates().to_numpy())
    
    print("The cell data contains {} genes.".format(gene_ids.size))
    return all_cell_genes, gene_ids




def get_gene_data(gene_data, gene_id):
    single_gene_data = gene_data.loc[(gene_data['GeneID'] == gene_id)]
    output = np.average(single_gene_data['Expression'].to_numpy())
    hm_matrix = single_gene_data.drop(['GeneID', 'BinID', 'Expression'], axis=1).to_numpy()
    return (hm_matrix, output)


def get_neighbors_data(gene_data, gene_id, gene_ids, N=10):
    gene_id_position = np.where(gene_ids == gene_id)[0][0]
    if (gene_id_position > N and gene_id_position < gene_ids.size - N):
        single_gene_data = gene_data.loc[(gene_data['GeneID'] >= gene_ids[gene_id_position-N]) & (gene_data['GeneID'] <= gene_ids[gene_id_position+N])]
        hm_matrices = single_gene_data.drop(['GeneID', 'BinID', 'Expression'], axis=1).to_numpy()
        return hm_matrices
    else:
        return np.array([[]])


def create_dataset(path='dataset/data/E100', test_size=0.33):
    gene_data, gene_ids = parse_all_cell_files(path)
    
    
    x_data = np.zeros((len(gene_ids), 100, 5), dtype='float32')
    y_data = np.zeros((len(gene_ids), 1), dtype='float32')
    
    
    for x, gene_id in enumerate(gene_ids):
        hm_matrix, expression = get_gene_data(gene_data, gene_id)
        x_data[x] = np.array(hm_matrix) 
        y_data[x] = np.array(expression)
    
    max_vals = np.max(np.max(x_data, axis = 1), axis = 0)
    
    x_data = np.asarray(x_data, dtype = 'float32')
    
    for idx, max_val in enumerate(max_vals):
        x_data[:,:,idx] /= max_val
     
    x_data*=2
    x_data-=1
    
    
    X_train, X_test, Y_train, Y_test = train_test_split(x_data, y_data, test_size=0.33)
    return X_train, X_test, Y_train, Y_test






