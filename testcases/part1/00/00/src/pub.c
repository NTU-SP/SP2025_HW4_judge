#include <stdio.h>
#include <stddef.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"

static int
foo(void *b __maybe_unused,
    struct message_metadata *m __maybe_unused,
    void *c __maybe_unused)
{
    static int is_called = 0;
    char d;

    if (!is_called) {
        scanf("%c", &d);
        is_called = 1;
    } else {
        pause();
    }

    return -1;
}

int
main()
{
    publisher_node("ExAmPlE522", foo, NULL);
    puts("[PUBLISHER SYNC END]");
    return 0;
}
