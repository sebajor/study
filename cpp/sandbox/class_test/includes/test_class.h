#include <string>

namespace class_test{
    class TestClass{
        private:
           int int_value {};
           float float_value {};
        public:
            int int_read {};
            std::string string_data {};

        TestClass(int int_start, float float_start);
        ~TestClass();
        float PrintData(std::string_view asd);
        int getIntValue(){return int_value;};
        float setIntValue(){return float_value;};
        };
}
