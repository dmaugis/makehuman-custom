#include <getopt.h>
#include <iostream>     // std::cout, std::fixed
#include <iomanip>      // std::setprecision
#include <algorithm>
#include <vector>
using namespace std;
#include <boost/filesystem.hpp>
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui_c.h>
using namespace cv;


int main(int argc, char** argv )
{
    Mat result;
    float sum_weight=0.0;
    for(int i=1; i<argc; i++) {        
        // read the source image file
        Mat imgsrc=imread(argv[i],1);
        if(imgsrc.empty()) {
            cerr << basename(argv[0]) << ": could not open file or invalid image file  '" << argv[i] << "'" << endl;
            exit(-1);
        }
        if(imgsrc.channels()!=3) {
            cerr << basename(argv[0]) << ": image file is not RGB '" << argv[i] << "'" << endl;
            exit(-1);
        }
        imgsrc.convertTo(imgsrc, CV_32FC1);
        
        i++;
        float weight=0;
        if(i<argc){
            weight=stof (string(argv[i]));
        }
        sum_weight+=weight;
        if(result.empty())
            result=imgsrc*weight;
        else
            result+=imgsrc*weight;
    }

    result=result/sum_weight;
    result.convertTo(result, CV_8UC3);
    imwrite("newskin.png",result);
    return 0;
}
