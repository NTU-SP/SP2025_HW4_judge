#include <stddef.h>
#include <string.h>

#include <unistd.h>

#include <hw4/utils.h>

#include "channel.h"

char content[] = "\xE3\x81\xA0\xE3\x81\x8B\xE3\x82\x89"
                 "\xE9\xA2\xA8\xE3\x81\xAB\xE5\x90\xB9"
                 "\xE3\x81\x8B\xE3\x82\x8C\xE3\x81\xA6"
                 "\xE3\x81\x84\xE3\x81\x93\xE3\x81\x86"
                 "\x0A\xE3\x83\x95\xE3\x82\xA3\xE3\x83"
                 "\xAB\xE3\x83\xA0\xE3\x81\xAF\xE7\x94"
                 "\xA8\xE6\x84\x8F\xE3\x81\x97\xE3\x81"
                 "\x9F\xE3\x82\x88\x0A\xE4\xB8\x80\xE7"
                 "\x94\x9F\xE5\x88\x86\xE3\x81\xAE\xE9"
                 "\x95\xB7\xE3\x81\x95\xE3\x82\x92\x20"
                 "\xE3\x81\x96\xE3\x81\xA3\xE3\x81\xA8"
                 "\x31\x31\x35\xE4\xB8\x87\xE3\x82\xAD"
                 "\xE3\x83\xAD";

static int
send_one(void *buffer, struct message_metadata *m, void *c __maybe_unused)
{
    static int is_sent = 0;
    char *buf = (char*)buffer;
    if (is_sent)
        pause();

    strcpy(buf, content);

    strcpy(m->name, "hyakujyugomankiro");
    m->len = sizeof(content) - 1;
    m->total_len = sizeof(content) - 1;
    m->offset = 0;

    is_sent = 1;

    return 0;
}

int
main()
{
    publisher_node("o", send_one, NULL);
    return 0;
}
