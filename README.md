<img width="558" height="390" alt="image" src="https://github.com/user-attachments/assets/57531a45-febe-4d75-aafa-67dbf75ebfaf" />


# Contents
[Introduction](#introduction)  
[Required Environment](#required-environment)  
[Data](#data)  
[Quick Start](#quick-start)  
[Citation](#citation)  


## Introduction
Modern agriculture demands precise genomic prediction to accelerate elite crop breeding, yet traditional genomic prediction approaches, such as genomic best linear unbiased prediction (GBLUP) and Bayesian methods, focus primarily on the cumulative effect of individual SNPs, thus neglecting the concerted influence that the surrounding sequence context has on the phenotype. To overcome these limitations, we propose two novel feature embedding modes (SNP-context and whole-genome) based on [DNABERT-2](https://github.com/MAGICS-LAB/DNABERT_2/tree/main), a cross-species genomic foundation model that uses self-attention mechanisms and transfer learning to automatically identify conserved sequence features across diverse evolutionary lineages without prior biological assumptions. 


## Required Environment

<pre> 
# Create a new Conda virtual environment with a custom name and specify Python version   
conda create -n env_name python=3.8

# activate virtual environment  
conda activate env_name  

# If you would like to use FlashAttention to get faster computation speeds and lower memory costs，you can install relative packages from source
git clone https://github.com/openai/triton.git;
cd triton/python;
pip install cmake; # build-time dependency
pip install -e .
pip install flash-attn
  
# Install all Python packages listed in the requirements.txt file
pip intall -r requirements.txt

# Run the main entry script
python entry.py

</pre>

Note：Before running the script, it is necessary to modify the configuration file params.ini according to your actual data situation.

<pre>
  
[path]
  # Path to pre-trained DNABERT-2 model files
  MODEL_PATH = /mnt/inspurfs/user-fs/experiment/DNABERT-2/DNABERT-2-117M

  # Path to variant sites (SNPs) data in pickle format
  VARIANT_SITE_PATH​= /mnt/inspurfs/user-fs/experiment/Rice/snposrice413.pkl

  # Directory containing FASTA files for crop genome sequences
  FASTA_BASE_DIR = /mnt/crop/rice413/413fasta/

  # File containing sample IDs for processing
  SAMPLE_ID_PATH = /mnt/inspurfs/user-fs/experiment/Rice/riceid413.txt

  # Output directories for SNP context embeddings with different window sizes
  OUTPUT_VECTOR_FILE_PATH_SNP = /mnt/inspurfs/user-fs/experiment/Rice/SNPvect/

  # Output directory for full sequence embeddings
  OUTPUT_VECTOR_FILE_PATH_FULL = /mnt/inspurfs/user-fs/experiment/Rice/Fullvect/  
  
  # A file containing combined genomic vectors and phenotypic traits, linked by sample IDs.
  CROP_VECTOR_TRAIT = /mnt/inspurfs/user-fs/experiment/vectortrait_rice413.csv

[value]
  # Number of sequences processed in parallel per GPU batch
  GPU_BATCH_SIZE = 512
  
  # Maximum sequence length for model input
  MAX_SEQ_LENGTH = 512
  
  # Prefix for SNP embedding output files
  OUTPUT_VECTOR_FILE_PREFIX_SNP = rice413_SNP_embedding
  
  # Prefix for full sequence embedding output files
  OUTPUT_VECTOR_FILE_PREFIX_FULL = rice413_full_embedding
  
  # Context window sizes (in nucleotides) around SNP variant sites
  CONTEXT_LEN = 500, 1000, 1500, 2000, 2500, 3000
</pre>


## Data
**1.Download crop genomic and phenotypic data**    
    We collected publicly available datasets of genome-wide SNP markers and phenotypic traits for three crop datasets—rice413, rice395, and maize301. The rice413 and rice395 datasets were both sourced from [Zhao, K., Tung, CW., Eizenga, G. et al. Genome-wide association mapping reveals a rich genetic architecture of complex traits in Oryza sativa. Nat Commun 2, 467 (2011). https://doi.org/10.1038/ncomms1467](https://www.nature.com/articles/ncomms1467) The maize301 dataset was obtained from the built-in dataset in [Tassel](https://pubmed.ncbi.nlm.nih.gov/17586829/) software. The reference genome used for the rice datasets was [IRGSP-1.0](https://plants.ensembl.org/Oryza_sativa/Info/Index), while the maize dataset was based on the [B73 RefGen_v5](https://plants.ensembl.org/Zea_mays/Info/Index) reference genome.

**2.Reconstructing whole-genome sequences**  
&emsp;&emsp;We developed a pipeline to reconstruct sample-specific whole-genome sequences by integrating variant data from a multi-sample Variant Call Format (VCF) file onto a reference genome. The workflow begins with essential preprocessing steps. The reference genome FASTA file is indexed via [samtools](https://github.com/samtools/samtools), and the VCF file is indexed via [bcftools](https://github.com/samtools/bcftools). These indexing procedures enable efficient, random-access lookups of genomic coordinates and variant records, which is critical for the performance of the subsequent steps.   
&emsp;&emsp;Next, a list of sample identifiers is extracted from the VCF header to enable automated, batch processing of all individuals. For each sample, a custom Python script, leveraging the [pysam](https://pypi.org/project/pysam/) and [pyfaidx](https://pypi.org/project/pyfaidx/) libraries, generates a personalized genome sequence. The script efficiently processes variants by iterating through the VCF records for a given sample. For each variant, it substitutes the reference allele with the sample-specific allele in a mutable copy of the reference sequence. The script efficiently processes variants by iterating through the VCF records for a given sample. For each variant, it substitutes the reference allele with the sample-specific allele in a mutable copy of the reference sequence.  
&emsp;&emsp;Finally, the generated FASTA files undergo a quality control (QC) check to ensure their integrity and accuracy. This QC involves programmatic validation of the FASTA format and a verification step where a random subset of variant positions in the output sequence is cross-referenced against the input VCF to confirm correct allele incorporation. The resulting high-quality whole-genome sequences provide a reliable foundation for subsequent whole-genome feature embedding.

## Quick Start

<pre>
import sys, os
from predict_crop_phenotype import predict
from configparser import ConfigParser
from generate_SNP_context_embedding import *
from generate_whole_genome_embedding import *
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "params.ini")
cf = ConfigParser()
cf.read('params.ini', encoding='utf-8')


# Obtain SNP context-based feature vectors
def get_SNP_context_embedding(basedir, sampleids):

    context_length = cf.get('value', 'CONTEXT_LEN').split(",")
    prefix = cf.get('value', 'OUTPUT_VECTOR_FILE_PREFIX_SNP')
    output_vector_file_path = cf.get('value', 'OUTPUT_VECTOR_FILE_PATH_SNP')

    dest = output_vector_file_path + prefix + str(contextlen) + ".csv"

    for cl in context_length:
        encodeSNP(basedir, sampleids, dest, cl)


# Obtain whole-genome feature vectors
def get_whole_genome_embedding(basedir, sampleids):

    prefix = cf.get('value', 'OUTPUT_VECTOR_FILE_PREFIX_FULL')
    output_vector_file_path = cf.get('value', 'OUTPUT_VECTOR_FILE_PATH_FULL')

    dest = output_vector_file_path + prefix + str(contextlen) + ".csv"

    encode_whole_genome(basedir, sampleids, dest)

  
samppath = cf.get('path', 'SAMPLE_ID_PATH')
sampleids = open(samppath, "r").read().splitlines()
basedir = cf.get('path', 'FASTA_BASE_DIR')

get_SNP_context_embedding(basedir, sampleids)

get_whole_genome_embedding(basedir, sampleids)

trait_names = ["Panicle number per plant", "Seed number per panicle", "Amylose content", "Alkali spreading value", "Protein content", "Seed length"]
# trait_names = ["Amylose.Content", "HULLED.SEED.LENGTH"]
# trait_names = ["EarHT", "dpoll", "EarDia"]
# Output the evaluation results of each GP model
predict(trait_names)  

</pre>


## Citation
If you find our research work helpful, please cite our paper.
<pre>
LI H, CUI Y, SUN T, WANG T, CHEN Z, WANG C, BIAN W, LIU J, WANG M, CHEN L, 2025. Research on crop phenotype prediction using SNP context and whole-genome feature embedding. bioRxiv: 2024-2025.
</pre>












