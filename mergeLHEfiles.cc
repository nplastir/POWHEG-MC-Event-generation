// g++ -Wall -o mergeLheFiles mergeLheFiles.cpp

#include <iostream>
#include <fstream>
#include <vector>



int main(int argc, char** argv)
{
  if(argc < 3)
  {
    std::cout << ">>>mergeLheFile.cpp::Usage:   " << argv[0] << "   initialFile.lhe   fileToAdd1.lhe   fileToAdd2.lhe ..." << std::endl;
    return -1;
  }
  
  char* initialFileName = argv[1]; 
  std::cout << "initialFileName = " << initialFileName << std::endl;
  
  std::vector<char*> fileToAddNames;
  for(int fileIt = 0; fileIt < argc-2; ++fileIt)
  {
    fileToAddNames.push_back( argv[2+fileIt] );
    std::cout << "fileToAddName = " << fileToAddNames.at(fileIt) << std::endl;
  }
  
  
  // open lhe file
  std::ifstream initialFile(initialFileName, std::ios::in);
  std::ofstream outFile("out.lhe", std::ios::out);
  std::ofstream weightIDFile("weightID.txt", std::ios::out);
  
  std::string line;
  std::string line2;
  bool writeEvent = false;
  bool changeWeightline = false;
  int eventIt = 0;
  int weightIDIt = 0;
  std::vector<std::string> weightID;
  
  // loop over initial file to write all the information contained in 
  // comments, header and init block
  while(!initialFile.eof())
  {
    getline(initialFile, line);
    
    //std::cout << line << std::endl;
    
    if( !initialFile.good() ) break;
    
    // readout the weightID !!!string of four digits!!! from <header> block
    //if( line.find("<weight id=") != std::string::npos )
    if( line.find("<weight id=") == 0)
    {
        //std::cout << "Position: " << line.find("<weight id=") << std::endl;
        std::string token = line.substr(line.find("\'")+1, 4);
        //std::cout << "ID: " << token << std::endl;
        weightIDFile << token << std::endl;
        weightID.push_back(token);
    }
    
    if( line != "</LesHouchesEvents>" ) 
    {        
        // start of the event's <weights> block
        if( line == "<weights>" )
        {
            outFile << "<rwgt>" << std::endl;
            //std::cout << "<rwgt>" << std::endl;
            changeWeightline = true;
            weightIDIt = 0;
            continue;
        }
        
        // end of <weights> block
        else if( line == "</weights>" )
        {
            outFile << "</rwgt>" << std::endl;
            //std::cout << "</rwgt>" << std::endl;
            weightIDIt = 0;
            changeWeightline = false;
        }
        
        // change the line with weight
        else if( changeWeightline == true )
        {
            outFile << "<wgt id=\'" << weightID.at(weightIDIt) << "\'>" << line << "</wgt>" << std::endl;
            //std::cout << "<wgt id=\'" << weightID.at(weightIDIt) << "\'>" << line << "</wgt>" << std::endl;
            weightIDIt++;
        }
        
        // all other lines write normally
        //~ if( line != "<weights>" && line != "</weights>" && changeWeightline == false )
        else
        {
            outFile << line << std::endl;
            //std::cout << line << std::endl;
        }
                
    }
    
    
    // end of the lhe file content
    if( line == "</LesHouchesEvents>" )
    {
      // loop over all other lhe files
      for(int fileIt = 0; fileIt < argc-2; ++fileIt)
      {
        std::ifstream fileToAdd(fileToAddNames.at(fileIt), std::ios::in);
        
        while(!fileToAdd.eof())
        {
            getline(fileToAdd, line2); 
            
            // decide whether to skip event or not 
            if( line2 == "<event>" )
            {
            ++eventIt;
            writeEvent = true;
            }
            
            // write line to outFile
            if(writeEvent == true)
            {                    
                // start of the event's <weights> block
                if( line2 == "<weights>" )
                {
                    outFile << "<rwgt>" << std::endl;
                    changeWeightline = true;
                    weightIDIt =0;
                    continue;
                }
                
                // end of <weights> block
                else if( line2 == "</weights>" )
                {
                    outFile << "</rwgt>" << std::endl;
                    weightIDIt = 0;
                    changeWeightline = false;
                }
                
                // change the line with weight
                else if( changeWeightline == true )
                {
                    outFile << "<wgt id=\'" << weightID.at(weightIDIt) << "\'>" << line2 << "</wgt>" << std::endl;
                    weightIDIt++;
                }
                
                // all other lines write normally
                //~ if( line2 != "<weights>" && line2 != "</weights>" && changeWeightline == false )
                else
                {
                    outFile << line2 << std::endl;
                }
                
            }
            
            
            // end of event
            if( line2 == "</event>" )
            writeEvent = false;
        }
      }
      outFile << "</LesHouchesEvents>" << std::endl;
    }    
    
  }
  
  
  std::cout << "Added " << eventIt << " events from " << argc-2 << " files to file " << initialFileName << std::endl;
  //std::ofstream cntFile("nevents.dat", std::ios::out);
  //cntFile << eventIt << std::endl;
  
  return 0;
}