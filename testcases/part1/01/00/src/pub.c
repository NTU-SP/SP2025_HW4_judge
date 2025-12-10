#include <stddef.h>
#include <string.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"

static int
send_one(void *buffer, struct message_metadata *m, void *c __maybe_unused)
{
    static int is_sent = 0;
    char *buf = (char*)buffer;
    if (is_sent)
        pause();

    memset(buf, '\0', 4096);
    buf[522] = 'S';
    buf[1126] = 'W';
    
    strcpy(m->name, "kimiwarokkuwokikanai");
    m->len = 1128;
    m->total_len = 2147483648;
    m->offset = 7777;

    is_sent = 1;

    return 0;
}

int
main()
{
    publisher_node("ExAmPlE522ExAmPlE522", send_one, NULL);
    return 0;
}
