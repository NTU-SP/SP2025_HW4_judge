#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#include <hw4/utils.h>
#include <hw4/sha256.h>

#include "channel.h"

void
dump_hash(void *msg_buf, struct message_metadata m, void *c __maybe_unused)
{
    char hash[SHA256_LEN + 1];
    char *buf = (char*)msg_buf;

    sha256(buf, m.len, hash);
    printf("%s:%s\n", m.name, hash);
    fflush(stdout);
}

int
main()
{
    subscriber_node("o", dump_hash, NULL);
    return 0;
}
