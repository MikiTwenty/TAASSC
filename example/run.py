# Standard Library
import os
import glob
import logging

# Local Modules
import taassc as lgr

# Set logger
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG level to capture detailed logs
    format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('taassc.log', mode='a'),
        logging.StreamHandler()])
logger = logging.getLogger('TAASSC')

# Ensure directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Sample Data Analyses
def sample_data_analysis(output_dir):
    try:
        ensure_dir(output_dir)

        # Analyze a sample text
        sample_text = "They said she liked hamburgers. They also said that he didn't."
        sample_try = lgr.LGR_Analysis(sample_text)

        # Display simple POS-specific lemmatized text
        logger.info(sample_try["lemma_text"])

        # Display count for "nn_all" category (all nouns)
        logger.info(sample_try["nn_all"])

        # Pretty-print tags
        lgr.print_vertical(sample_try["tagged_text"])

        # Write vertical output to file
        tsv_output_path = os.path.join(output_dir, "sample_try.tsv")
        lgr.output_vertical(sample_try["tagged_text"], tsv_output_path, ordered_output="full")

        # Write XML output to file
        xml_output_path = os.path.join(output_dir, "sample_try.xml")
        lgr.output_xml(sample_try["tagged_text"], xml_output_path)
    except Exception as e:
        logger.exception(f"Error in sample data analysis: {e}")

# Full Data Analysis
def full_data_analysis(folder, output_base_dir):
    try:
        # Generate file list for analysis
        file_list = glob.glob(f"{folder}/*.txt")

        if not file_list:
            logger.warning(f"No text files found in the folder: {folder}")
            return

        ensure_dir(output_base_dir)

        csv_output_path = os.path.join(output_base_dir, "results.csv")

        # Perform full analysis and save results
        logger.info(f"Starting full analysis on {len(file_list)} files.")
        lgr.LGR_Full(file_list, csv_output_path, output=["xml", "vertical"], outdirname=output_base_dir)

        logger.info(f"Analysis complete.")
    except Exception as e:
        logger.exception(f"Error in full data analysis: {e}")

# Main function to run all analyses
def main():
    # Specify the input and output directories here
    DATA_DIR = "data/test_files"
    OUTPUT_DIR = "data/output"

    sample_output_dir = os.path.join(OUTPUT_DIR, "sample_data")
    full_output_dir = os.path.join(OUTPUT_DIR, "full_data")

    sample_data_analysis(sample_output_dir)
    full_data_analysis(DATA_DIR, full_output_dir)

if __name__ == "__main__":
    main()