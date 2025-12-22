#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"

void
recv_msg(void *msg_buf, struct message_metadata m __maybe_unused, void *c)
{
    static int nr_recvs = 0;
    static int target = -1;

    if (target == -1)
        target = (int)c;

    nr_recvs++;
    if (nr_recvs == target) {
        puts("OK");
        fflush(stdout);
        nr_recvs = 0;
    }
}

int
main(int argc, char *argv[])
{
    if (argc != 3 || strlen(argv[1]) > CHANNEL_MAX_NAME_LEN)
        ERROR_EXIT("Usage: %s <channel name (<= %d chars)> <nr_blocks>\n",
                   argv[0], CHANNEL_MAX_NAME_LEN);

    subscriber_node(argv[1], recv_msg, (void*)atoi(argv[2]));
    
    return 0;
}
