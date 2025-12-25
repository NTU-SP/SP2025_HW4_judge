#include <stdio.h>
#include <stddef.h>
#include <string.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"

static int
send_blks(void *b __maybe_unused, struct message_metadata *m, void *c __maybe_unused)
{
    static int nr_called = 0;

    if (nr_called < 64) {
        m->name[0] = 'c';
        m->name[1] = '\0';
        m->len = 4096;
        m->total_len = 4096 * 64;
        m->offset = nr_called * 4096;
        nr_called++;
    } else {
        pause();
    }

    return 0;
}

int
main(int argc, char *argv[])
{
    if (argc != 2 || strlen(argv[1]) > CHANNEL_MAX_NAME_LEN)
        ERROR_EXIT("Usage: %s <channel name (<= %d chars)>\n",
                   argv[0], CHANNEL_MAX_NAME_LEN);

    publisher_node(argv[1], send_blks, NULL);
    return 0;
}
