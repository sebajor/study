#include "../includes/test_class.h"
#include <string>
#include <iostream>

int main(){

    class_test::TestClass test(1,1);

    std::string asd {"asdsad"};
    std::string_view qwe {asd};
    
    test.PrintData(qwe);

    return 1;
}

