#include <stddef.h>
#include <string.h>

#include <hw4/utils.h>

#include "channel.h"

char content[] = "\xE6\x84\x9B\xE3\x81\xA8\xE3\x81\x8B"
                 "\xE6\x81\x8B\xE3\x81\xA8\xE3\x81\x8B"
                 "\xE3\x81\xAE\xE8\xA8\x80\xE8\x91\x89"
                 "\xE3\x81\xA7\xE7\x89\x87\xE4\xBB\x98"
                 "\xE3\x81\x91\xE3\x82\x89\xE3\x82\x8C"
                 "\xE3\x81\xAA\xE3\x81\x84\xE3\x81\x8F"
                 "\xE3\x82\x89\xE3\x81\x84\xE3\x81\xAE"
                 "\x0A\xE6\x84\x9B\xE3\x81\x97\xE3\x81"
                 "\xA6\xE3\x82\x8B\xE3\x81\x8C\x20\xE6"
                 "\xBA\xA2\xE3\x82\x8C\xE5\x87\xBA\xE3"
                 "\x81\x97\xE3\x81\xA6\x20\xE6\xAD\xA2"
                 "\xE3\x81\xBE\xE3\x82\x89\xE3\x81\xAA"
                 "\xE3\x81\x84\xE6\x83\xB3\xE3\x81\x84";

static int
send_one(void *buffer, struct message_metadata *m, void *c __maybe_unused)
{
    static int is_sent = 0;
    char *buf = (char*)buffer;
    if (is_sent)
        return -1;

    strcpy(buf, content);

    strcpy(m->name, "aitokakoitoka");
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
