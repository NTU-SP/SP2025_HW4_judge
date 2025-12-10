#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>

#include <hw4/utils.h>

#include "channel.h"

static int
very_cute_trans(uint64_t n)
{
    const int k1 = 1150000 % 511;
    const int k2 = 0x052519 % 511;
    const int a = (k1 ^ k2) % 97 + 3;
    return ((n * a) + (k2 - k1)) % 511;
}

static char *names[] = {
    "bokuwanankaidatte",
    "nanjukkaidatte",
    "kimitodakiatte tewo",
    "tsunaidekisuwoshita"
};

static int off[][2] = {
    {123, 432}, {987, 344}, {244, 717}, {42, 300}
};

static int
get_idx(char *name)
{
    for (int i = 0; i < 4; ++i) {
        if (strcmp(name, names[i]) == 0)
            return i;
    }
    return 0; // arbitrary
}

void
log_msg_one_line(void *msg_buf, struct message_metadata m, void *c __maybe_unused)
{
    char *buf = (char*)msg_buf;
    int idx = get_idx(m.name);

    printf("%s;%"PRIu32";%"PRIu64";%"PRIu64";%d;%d\n",
           m.name, m.len, m.total_len, m.offset,
           (buf[very_cute_trans(off[idx][0] + ((m.offset / 522) << idx))] == 'S'),
           (buf[very_cute_trans(off[idx][1] + ((m.offset / 522) << idx))] == 'W'));
    fflush(stdout);
}

int
main()
{
    subscriber_node("V3rYCu73Ch@nNe2", log_msg_one_line, NULL);
    return 0;
}
