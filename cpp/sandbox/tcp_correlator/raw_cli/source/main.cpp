#include "../includes/correlator.h"
#include <iostream>




int parse_args(int argc, char* argv[], hyperparameters &params){
    for(int i=1; i<argc; ++i){
        try{
            std::string arg = argv[i];
            if(arg == "--port" && (i+1)<argc)
                params.port = std::stoi(argv[++i]);
            else if(arg == "--ip" && (i+1)<argc)
                params.ip = std::string_view(argv[++i]);
            else if(arg == "--max_workers" && (i+1)<argc)
                params.max_workers = std::stoi(argv[++i]);
            else if(arg == "--accumulation" && (i+1)<argc)
                params.accumulation = std::stoi(argv[++i]);
            else if(arg == "--fft_points" && (i+1)<argc)
                params.fft_points = std::stoi(argv[++i]);
            else if(arg == "LO" && (i+1)<argc)
                params.LO = std::stof(argv[++i]);
            else if(arg == "BW" && (i+1)<argc)
                params.BW = std::stof(argv[++i]);
        }
        catch(const std::exception &e){
            std::cout << "Data thread exception: "<< e.what() << "\n";
            std::cout << "Error in parameter "<< argv[i] << "\n";
            }
    }
    return 1;

}


int main(int argc, char* argv[]){
    hyperparameters params;
    parse_args(argc, argv, params);
    std::cout << "ip: "<<params.ip <<"\n";
    std::cout << "port: "<<params.port <<"\n";
    std::cout << "max_workers: "<<params.max_workers<<"\n";
    std::cout << "accumulation: "<<params.accumulation<<"\n";
    std::cout << "fft_points: "<<params.fft_points<<"\n";
    std::cout << "LO: "<<params.LO<<"\n";
    std::cout << "BW: "<<params.BW<<"\n\n";

    std::cout << "Creting correlator obj..";
    Correlator corr(params);
    std::cout << "done\n";
    std::cout << "starting while True loop\n";
    corr.run();
}

