#include "Thread.h"



#ifdef __x86_64__
/* code for 64 bit Intel arch */

typedef unsigned long address_t;
#define JB_SP 6
#define JB_PC 7

/* A translation is required when using an address of a variable.
   Use this as a black box in your code. */
address_t translate_address(address_t addr)
{
    address_t ret;
    asm volatile("xor    %%fs:0x30,%0\n"
                 "rol    $0x11,%0\n"
    : "=g" (ret)
    : "0" (addr));
    return ret;
}

#else
/* code for 32 bit Intel arch */

typedef unsigned int address_t;
#define JB_SP 4
#define JB_PC 5

/* A translation is required when using an address of a variable.
   Use this as a black box in your code. */
address_t translate_address(address_t addr)
{
    address_t ret;
    asm volatile("xor    %%gs:0x18,%0\n"
		"rol    $0x9,%0\n"
                 : "=g" (ret)
                 : "0" (addr));
    return ret;
}

#endif


Thread::Thread(int id, void (*func)(void), int priority_quanta_length) : _id(id), _func(func),
                                                         _priority_quanta_length(priority_quanta_length){
    _status = "READY";
    _is_alive = true;

    try {
        _stack = new char[STACK_SIZE];
    }
    catch (std::bad_alloc& ba){
        std::cerr << "system error: bad memory allocation" << std::endl;
        exit(1);
    }

    _quanta_count =0;
    if (_stack == nullptr){
        std::cerr << "system error: could not allocate memory" << std::endl;
        exit(1);
    }

    // initialize environment
    address_t sp, pc;

    sp = (address_t) _stack + STACK_SIZE - sizeof(address_t);
    pc = (address_t) _func;

    sigsetjmp(_env, 1);
    (_env->__jmpbuf)[JB_SP] = translate_address(sp);
    (_env->__jmpbuf)[JB_PC] = translate_address(pc);
    sigemptyset(&_env->__saved_mask);
}


Thread::~Thread() {
    delete[] _stack;
}

int Thread::get_id() {
    return _id;
}

int Thread::get_quanta_count(){
    return _quanta_count;
}

std::string Thread::get_status() {
    return _status;
}

void Thread::set_status(std::string status) {
    _status = status;
}

void Thread::increment_quanta() {
    _quanta_count += 1;
}

void Thread::set_quanta_length(int quanta_length){
    _priority_quanta_length = quanta_length;
}

int Thread::get_quanta_length(){
    return _priority_quanta_length;
}

void Thread::set_is_alive_false() {
    _is_alive = false;
}

bool Thread::get_is_alive(){
    return _is_alive;
}

sigjmp_buf& Thread::get_env()
{
    return _env;
}
