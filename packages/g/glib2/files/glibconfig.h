#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "../lib32/glib-2.0/include/glibconfig.h"
#elif __WORDSIZE == 64
#include "../lib64/glib-2.0/include/glibconfig.h"
#else
#error "Unknown word size"
#endif
