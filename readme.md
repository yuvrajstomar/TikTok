####################################################################################################################
TikTok Data Scraping -- DATA Initiative Research Lab --- Group 1
####################################################################################################################

Please find steps to running the Scraping script:
    
	1. Download Miniconda3 Python version 3.8 -- follow installation guide 
    	2. Download PyCharm Community version -- follow Installation guide -- Configure your conda Python interpreter
    	3. Open PyCharm IDE -> Open "VCS" -> Open "Get from Version Control.." -> 
						Enter URL : https://github.com/kraken111/TikTok -> Click "Clone"
    	4. Open "Terminal" -> Run following command : "bash run.sh" (it will setup your environment)
   	5. Run command: "conda activate selenium_env" (it will activate the environment)
    	6 .Download geckodriver for Mozilla Firefox -> update the file path in tiktok.py file
    	7. Read the comments in the tiktok.py main method before running the script
    	8. Run the script cmd: "python3 tiktok.py"

	Note:	1. Make sure to download Mozilla firebox in your system
		2. Use Pycharm or Syder since the geckodriver won't work in Jupyter notebook or Google Colab environment
		3. There might be timeout issues while running the script mostly because of web page loading 
		   (in that case increase the delays or reach out for help)
		4. Update path for geckodriver/ source.xlsx file
		5. While running the script there will be a metadata csv file will be generated in the end + 
		   userwise folders will be created containing .mp4 videoclips 

########################################################################################################################
