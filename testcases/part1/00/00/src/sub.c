#include <stddef.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"


static void
foo(void *b __maybe_unused,
    struct message_metadata m __maybe_unused,
    void *c __maybe_unused)
{
    pause();
}

int
main()
{
    subscriber_node("ExAmPlE522", foo, NULL);
    return 0;
}
