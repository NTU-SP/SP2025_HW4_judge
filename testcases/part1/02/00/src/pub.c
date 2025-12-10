#include <stddef.h>
#include <string.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"

static int nr_to_send;

static int
very_cute_trans(int n)
{
    const int k1 = 1150000 % 511;
    const int k2 = 0x052519 % 511;
    const int a = (k1 ^ k2) % 97 + 3;
    return ((n * a) + (k2 - k1)) % 511;
}

static int
send_some(void *buffer, struct message_metadata *m, void *c __maybe_unused)
{
    static int nr_sent = 0;
    char *buf = (char*)buffer;
    
    if (nr_sent >= nr_to_send)
        pause();

    memset(buf, '\0', 4096);
    buf[very_cute_trans(1671 + nr_sent)] = 'S';
    buf[very_cute_trans(3317 + nr_sent)] = 'W';

    strcpy(m->name, "watashiwaasagakirai");
    m->len = 522;
    m->total_len = (uint64_t)nr_to_send * 522;
    m->offset = (uint64_t)nr_sent * 522;

    nr_sent++;

    return 0;
}

int
main(int argc, char *argv[])
{
    if (argc != 2)
        return 3;
    nr_to_send = atoi(argv[1]);
    publisher_node("V3rYCu73Ch@nNe2", send_some, NULL);
    return 0;
}
