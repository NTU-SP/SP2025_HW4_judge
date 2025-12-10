#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"

static uint64_t nr_to_send[4];

static int
very_cute_trans(uint64_t n)
{
    const int k1 = 1150000 % 511;
    const int k2 = 0x052519 % 511;
    const int a = (k1 ^ k2) % 97 + 3;
    return ((n * a) + (k2 - k1)) % 511;
}

static int
send_some(void *buffer, struct message_metadata *m, void *c __maybe_unused)
{
    static uint64_t nr_sent = 0;
    static int phase = 0;
    char b;
    char *buf = (char*)buffer;
    
    if (nr_sent >= nr_to_send[phase]) {
        scanf("%c", &b);
        puts("[PUBLISHER SYNC WAKEUP]");
        fflush(stdout);
        phase++;
        nr_sent = 0;
    }

    switch (phase)
    {
    case 0:
        memset(buf, '\0', 4096);
        buf[very_cute_trans(123 + (nr_sent << phase))] = 'S';
        buf[very_cute_trans(432 + (nr_sent << phase))] = 'W';

        strcpy(m->name, "bokuwanankaidatte");
        m->len = 522;
        m->total_len = nr_to_send[0] * 522;
        m->offset = nr_sent * 522;

        nr_sent++;
    
        break;

    case 1:
        memset(buf, '\0', 4096);
        buf[very_cute_trans(987 + (nr_sent << phase))] = 'S';
        buf[very_cute_trans(344 + (nr_sent << phase))] = 'W';

        strcpy(m->name, "nanjukkaidatte");
        m->len = 522;
        m->total_len = nr_to_send[1] * 522;
        m->offset = nr_sent * 522;

        nr_sent++;
    
        break;

    case 2:
        memset(buf, '\0', 4096);
        buf[very_cute_trans(244 + (nr_sent << phase))] = 'S';
        buf[very_cute_trans(717 + (nr_sent << phase))] = 'W';

        strcpy(m->name, "kimitodakiatte tewo");
        m->len = 522;
        m->total_len = nr_to_send[2] * 522;
        m->offset = nr_sent * 522;

        nr_sent++;
    
        break;

    case 3:
        memset(buf, '\0', 4096);
        buf[very_cute_trans(42 + (nr_sent << phase))] = 'S';
        buf[very_cute_trans(300 + (nr_sent << phase))] = 'W';

        strcpy(m->name, "tsunaidekisuwoshita");
        m->len = 522;
        m->total_len = nr_to_send[3] * 522;
        m->offset = nr_sent * 522;

        nr_sent++;

        break;

    case 4:
        pause();
        break;

    default:
        break;
    }
    
    return 0;
}

int
main(int argc, char *argv[])
{
    if (argc != 5)
        return 3;

    nr_to_send[0] = strtoull(argv[1], NULL, 10);
    nr_to_send[1] = strtoull(argv[2], NULL, 10);
    nr_to_send[2] = strtoull(argv[3], NULL, 10);
    nr_to_send[3] = strtoull(argv[4], NULL, 10);

    publisher_node("V3rYCu73Ch@nNe2", send_some, NULL);
    return 0;
}
