#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#include <hw4/utils.h>

#include "channel.h"

void
dump_msg(void *msg_buf, struct message_metadata m, void *c __maybe_unused)
{
    char *buf = (char*)msg_buf;

    for (uint32_t i = 0; i < m.len; ++i)
        printf("\\x%02x", (unsigned char)buf[i]);
    printf("\n");
    fflush(stdout);
}

int
main()
{
    subscriber_node("o", dump_msg, NULL);
    return 0;
}
