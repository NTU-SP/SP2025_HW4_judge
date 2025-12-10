#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#include <hw4/utils.h>
#include <hw4/sha256.h>

#include "channel.h"

void
check_msg(void *msg_buf, struct message_metadata m, void *c __maybe_unused)
{
    char hash[SHA256_LEN + 1];
    char *buf = (char*)msg_buf;

    sha256(buf, m.len, hash);

    printf("name: %s\n"
           "len: %"PRIu32"\n"
           "total len: %"PRIu64"\n"
           "offset: %"PRIu64"\n"
           "hash: %s\n"
           "%d %d\n",
           m.name, m.len, m.total_len, m.offset, hash,
           (buf[522] == 'S'), (buf[1126] == 'W'));
    fflush(stdout);
}

int
main()
{
    subscriber_node("ExAmPlE522ExAmPlE522", check_msg, NULL);
    return 0;
}
