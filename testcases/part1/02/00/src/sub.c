#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#include <hw4/utils.h>

#include "channel.h"

static int
very_cute_trans(int n)
{
    const int k1 = 1150000 % 511;
    const int k2 = 0x052519 % 511;
    const int a = (k1 ^ k2) % 97 + 3;
    return ((n * a) + (k2 - k1)) % 511;
}


void
log_msg_one_line(void *msg_buf, struct message_metadata m, void *c __maybe_unused)
{
    char *buf = (char*)msg_buf;

    printf("%s;%"PRIu32";%"PRIu64";%"PRIu64";%d;%d\n",
           m.name, m.len, m.total_len, m.offset,
           (buf[very_cute_trans(1671 + (m.offset / 522))] == 'S'),
           (buf[very_cute_trans(3317 + (m.offset / 522))] == 'W'));
    fflush(stdout);
}

int
main()
{
    subscriber_node("V3rYCu73Ch@nNe2", log_msg_one_line, NULL);
    return 0;
}
