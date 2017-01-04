import sys, getopt, time
import reviewXML


def main(argv):

   # check if the python version is >3 or not, otherwise let the user know about it and exit
   if(sys.version_info[0] <3):
      print('Your Python version i.e., '+str(sys.version_info[0]) +' is not compatible with this utility.')
      print('Please upgrade to Python 3.x onwards!')
      sys.exit()
   #----------------------------------------------------------------------------------------

   inputfile = ''
   prMsg =''
   
   try:
      opts, args = getopt.getopt(argv,"hi:r",["ifile=","pType="])      
   except getopt.GetoptError:
      print('Invalid argument passed! \n');
      print('Example: xmlPortfolio.py -i <inputfile.xml> <-r or some other flag to tell what to do with XML>');
      sys.exit(2)

   for opt, arg in opts:
      # for help command -h
      if opt == '-h':  
         print('Format of arguments:');
         print('xmlPortfolio.py -i <inputfile.xml> -r');
         print('-R: for xml review of unique layouts and strategies etc.');
         sys.exit()

      # input file -i
      elif opt in ("-i", "--ifile"):
         inputfile = arg
         if(inputfile[-4:] != '.xml'):
            print('XML files can only be processed!');
            sys.exit();

      # if -r is entered then it means review XML
      elif opt in ("-r", "--pType"):
         prMsg = 'Input File: "'+inputfile +'"\n'
         prMsg = prMsg +'Action: REVIEW \n'
   
   print('');
   print('');   
   prMsg = prMsg +'Please press "Enter" key on your Keyboard to proceed:'

   if(str(input(prMsg)) !=''):
      sys.exit();
   else:
      print('Processing... \n\n');      
      time.sleep(0.3)
   
   reviewXML.parseXML(inputfile); # Call this function to parse XML


if __name__ == "__main__":
   main(sys.argv[1:])