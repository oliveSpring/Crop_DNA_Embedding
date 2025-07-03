import sys, os
from predict_crop_phenotype import predict
from configparser import ConfigParser
from generate_SNP_context_embedding import *
from generate_whole_genome_embedding import *
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params.ini")
cf = ConfigParser()
cf.read('params.ini', encoding='utf-8')


#获取SNP上下文特征向量
def get_SNP_context_embedding(basedir, sampleids):

    context_length = cf.get('value', 'CONTEXT_LEN').split(",")
    prefix = cf.get('value', 'OUTPUT_VECTOR_FILE_PREFIX_SNP')
    output_vector_file_path = cf.get('value', 'OUTPUT_VECTOR_FILE_PATH_SNP')

    dest = output_vector_file_path + prefix + str(contextlen) + ".csv"

    for cl in context_length:
        encodeSNP(basedir, sampleids, dest, cl)


#获取全基因组特征向量
def get_whole_genome_embedding(basedir, sampleids):

    prefix = cf.get('value', 'OUTPUT_VECTOR_FILE_PREFIX_FULL')
    output_vector_file_path = cf.get('value', 'OUTPUT_VECTOR_FILE_PATH_FULL')

    dest = output_vector_file_path + prefix + str(contextlen) + ".csv"

    encode_whole_genome(basedir, sampleids, dest)



def main():

    samppath = cf.get('path', 'SAMPLE_ID_PATH')
    sampleids = open(samppath, "r").read().splitlines()
    basedir = cf.get('path', 'FASTA_BASE_DIR')

    get_SNP_context_embedding(basedir, sampleids)
    get_whole_genome_embedding(basedir, sampleids)

    trait_names = ["Panicle number per plant", "Seed number per panicle", "Amylose content", "Alkali spreading value", "Protein content", "Seed length"]
    # trait_names = ["Amylose.Content", "HULLED.SEED.LENGTH"]
    # trait_names = ["EarHT", "dpoll", "EarDia"]
    predict(trait_names)  #输出每个GP模型评估结果







if __name__ == "__main__":
    main()



