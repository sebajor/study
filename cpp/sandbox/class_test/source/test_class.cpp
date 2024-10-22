#include <string>
#include <iostream>
#include "../includes/test_class.h"

namespace class_test{

    //class constructor
    TestClass::TestClass(int int_start, float float_start){
       int_value=int_start;
       float_value=float_start;
       std::cout << "class constructor\n";
    }
   //class destructor 
    TestClass::~TestClass(){
       std::cout << "class destructor\n";
   }

    float TestClass::PrintData(std::string_view asd){
        std::cout << asd << "\n";
        return 0;
    }
}

