#define _POSIX_C_SOURCE 200809L
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define HEADER_SIZE 25
#define FNV_OFFSET 1469598103934665603ULL
#define FNV_PRIME 1099511628211ULL

typedef unsigned __int128 u128;
static u128 CH[129][129];

typedef struct {
    const uint8_t *p;
    size_t n;
    size_t bit;
} BitReader;

typedef struct {
    const uint8_t *data;
    size_t size;
    uint8_t bits;
    uint16_t group_size;
    uint16_t stride;
    uint32_t blocks;
    uint32_t index_count;
    uint64_t weights;
    const uint8_t *index_bytes;
    size_t data_start;
} BPE;

typedef struct {
    uint64_t lo;
    uint64_t hi;
} Mask;

static uint16_t rd16(const uint8_t *p) {
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static uint32_t rd32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) |
           ((uint32_t)p[3] << 24);
}

static uint64_t rd64(const uint8_t *p) {
    uint64_t value = 0;
    for (int index = 7; index >= 0; index--) {
        value = (value << 8) | p[index];
    }
    return value;
}

static void init_combinations(void) {
    for (int n = 0; n <= 128; n++) {
        CH[n][0] = 1;
        CH[n][n] = 1;
        for (int k = 1; k < n; k++) {
            CH[n][k] = CH[n - 1][k - 1] + CH[n - 1][k];
        }
    }
}

static int ceil_log2_u128(u128 value) {
    if (value <= 1) {
        return 0;
    }
    value--;
    int bits = 0;
    while (value) {
        bits++;
        value >>= 1;
    }
    return bits;
}

static int ceil_log2_u32(uint32_t value) {
    if (value <= 1) {
        return 0;
    }
    value--;
    int bits = 0;
    while (value) {
        bits++;
        value >>= 1;
    }
    return bits;
}

static uint64_t read_u64(BitReader *reader, int bits) {
    uint64_t value = 0;
    for (int index = 0; index < bits; index++) {
        if (reader->bit >= reader->n * 8) {
            fprintf(stderr, "truncated bitstream\n");
            exit(2);
        }
        size_t byte_index = reader->bit >> 3;
        int bit_index = (int)(reader->bit & 7);
        value |= (uint64_t)((reader->p[byte_index] >> bit_index) & 1u) << index;
        reader->bit++;
    }
    return value;
}

static u128 read_u128(BitReader *reader, int bits) {
    u128 value = 0;
    for (int index = 0; index < bits; index++) {
        if (reader->bit >= reader->n * 8) {
            fprintf(stderr, "truncated bitstream\n");
            exit(2);
        }
        size_t byte_index = reader->bit >> 3;
        int bit_index = (int)(reader->bit & 7);
        value |= (u128)((reader->p[byte_index] >> bit_index) & 1u) << index;
        reader->bit++;
    }
    return value;
}

static void mask_set(Mask *mask, int position) {
    if (position < 64) {
        mask->lo |= 1ULL << position;
    } else {
        mask->hi |= 1ULL << (position - 64);
    }
}

static int mask_get(Mask mask, int position) {
    if (position < 64) {
        return (int)((mask.lo >> position) & 1ULL);
    }
    return (int)((mask.hi >> (position - 64)) & 1ULL);
}

static Mask all_ones(int n) {
    Mask mask = {0, 0};
    if (n >= 64) {
        mask.lo = UINT64_MAX;
        int rest = n - 64;
        mask.hi = rest == 64 ? UINT64_MAX : (rest ? ((1ULL << rest) - 1) : 0);
    } else if (n) {
        mask.lo = (1ULL << n) - 1;
    }
    return mask;
}

static Mask decode_plane(BitReader *reader, int n) {
    int mode = (int)read_u64(reader, 2);
    Mask mask = {0, 0};
    if (mode == 0) {
        return mask;
    }
    if (mode == 1) {
        return all_ones(n);
    }
    if (mode == 2) {
        for (int position = 0; position < n; position++) {
            if (read_u64(reader, 1)) {
                mask_set(&mask, position);
            }
        }
        return mask;
    }

    int count_bits = ceil_log2_u32((uint32_t)n + 1);
    int k = (int)read_u64(reader, count_bits);
    if (k <= 0 || k >= n) {
        fprintf(stderr, "invalid enumerative population k=%d n=%d\n", k, n);
        exit(2);
    }
    u128 combinations = CH[n][k];
    int rank_bits = ceil_log2_u128(combinations);
    u128 rank = read_u128(reader, rank_bits);
    if (rank >= combinations) {
        fprintf(stderr, "invalid enumerative rank\n");
        exit(2);
    }

    int x = n - 1;
    for (int index = k; index >= 1; index--) {
        while (x >= 0 && CH[x][index] > rank) {
            x--;
        }
        if (x < 0) {
            fprintf(stderr, "enumerative unrank failed\n");
            exit(2);
        }
        mask_set(&mask, x);
        rank -= CH[x][index];
        x--;
    }
    if (rank) {
        fprintf(stderr, "enumerative unrank residual\n");
        exit(2);
    }
    return mask;
}

static uint64_t fnv_quantized(uint64_t hash, int16_t value) {
    uint16_t raw = (uint16_t)value;
    hash ^= (uint8_t)(raw & 255);
    hash *= FNV_PRIME;
    hash ^= (uint8_t)(raw >> 8);
    hash *= FNV_PRIME;
    return hash;
}

static uint64_t decode_payload(
    const uint8_t *payload,
    size_t payload_length,
    int n,
    int bits,
    uint64_t hash
) {
    BitReader reader = {payload, payload_length, 0};
    Mask sign = decode_plane(&reader, n);
    int16_t values[128] = {0};

    for (int plane_index = 0; plane_index < bits - 1; plane_index++) {
        Mask plane = decode_plane(&reader, n);
        for (int index = 0; index < n; index++) {
            if (mask_get(plane, index)) {
                values[index] |= (int16_t)(1 << plane_index);
            }
        }
    }

    for (int index = 0; index < n; index++) {
        if (mask_get(sign, index) && values[index]) {
            values[index] = -values[index];
        }
        hash = fnv_quantized(hash, values[index]);
    }
    return hash;
}

static int parse_bpe(BPE *bpe, const uint8_t *data, size_t size) {
    if (size < HEADER_SIZE || memcmp(data, "BPE1", 4)) {
        return 0;
    }
    bpe->data = data;
    bpe->size = size;
    bpe->bits = data[4];
    bpe->group_size = rd16(data + 5);
    bpe->stride = rd16(data + 7);
    bpe->blocks = rd32(data + 9);
    bpe->weights = rd64(data + 13);
    bpe->index_count = rd32(data + 21);
    bpe->index_bytes = data + HEADER_SIZE;
    bpe->data_start = HEADER_SIZE + (size_t)bpe->index_count * 8;
    return bpe->data_start <= size;
}

static uint64_t bpe_index(const BPE *bpe, uint32_t index) {
    return rd64(bpe->index_bytes + (size_t)index * 8);
}

static uint64_t decode_bpe_all(const BPE *bpe) {
    size_t position = bpe->data_start;
    uint64_t hash = FNV_OFFSET;
    uint64_t weights = 0;
    for (uint32_t block = 0; block < bpe->blocks; block++) {
        if (position + 2 > bpe->size) {
            exit(2);
        }
        int n = bpe->data[position] + 1;
        int payload_length = bpe->data[position + 1];
        if (position + 2 + (size_t)payload_length > bpe->size) {
            exit(2);
        }
        hash = decode_payload(
            bpe->data + position + 2,
            (size_t)payload_length,
            n,
            bpe->bits,
            hash
        );
        weights += (uint64_t)n;
        position += 2 + (size_t)payload_length;
    }
    if (weights != bpe->weights) {
        fprintf(stderr, "decoded weight count mismatch\n");
        exit(2);
    }
    return hash;
}

static int sign_magnitude_decode(uint8_t code, int bits) {
    int sign = code >> (bits - 1);
    int magnitude = code & ((1 << (bits - 1)) - 1);
    return sign && magnitude ? -magnitude : magnitude;
}

static uint8_t fixed_code_at(const uint8_t *data, uint64_t index, int bits) {
    if (bits == 8) {
        return data[index];
    }
    uint8_t byte = data[index >> 1];
    return index & 1 ? (byte >> 4) : (byte & 15);
}

static uint64_t decode_fixed_all(const uint8_t *data, uint64_t weights, int bits) {
    uint64_t hash = FNV_OFFSET;
    for (uint64_t index = 0; index < weights; index++) {
        int value = sign_magnitude_decode(fixed_code_at(data, index, bits), bits);
        hash = fnv_quantized(hash, (int16_t)value);
    }
    return hash;
}

static double now_seconds(void) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (double)now.tv_sec + now.tv_nsec * 1e-9;
}

static int compare_double(const void *left, const void *right) {
    double a = *(const double *)left;
    double b = *(const double *)right;
    return a < b ? -1 : a > b;
}

static uint64_t xorshift64(uint64_t *state) {
    uint64_t value = *state;
    value ^= value << 13;
    value ^= value >> 7;
    value ^= value << 17;
    *state = value;
    return value;
}

static uint64_t decode_bpe_random(
    const BPE *bpe,
    uint32_t target,
    uint64_t hash
) {
    uint32_t superblock = target / bpe->stride;
    uint32_t current = superblock * bpe->stride;
    size_t position = (size_t)bpe_index(bpe, superblock);
    while (current < target) {
        int payload_length = bpe->data[position + 1];
        position += 2 + (size_t)payload_length;
        current++;
    }
    int n = bpe->data[position] + 1;
    int payload_length = bpe->data[position + 1];
    return decode_payload(
        bpe->data + position + 2,
        (size_t)payload_length,
        n,
        bpe->bits,
        hash
    );
}

static uint8_t *read_file(const char *path, size_t *size) {
    FILE *handle = fopen(path, "rb");
    if (!handle) {
        perror(path);
        exit(2);
    }
    fseek(handle, 0, SEEK_END);
    long length = ftell(handle);
    rewind(handle);
    uint8_t *data = malloc((size_t)length);
    if (!data) {
        exit(2);
    }
    if (fread(data, 1, (size_t)length, handle) != (size_t)length) {
        exit(2);
    }
    fclose(handle);
    *size = (size_t)length;
    return data;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s file.bpe fixed.bin\n", argv[0]);
        return 2;
    }
    init_combinations();

    size_t bpe_size;
    size_t fixed_size;
    uint8_t *bpe_data = read_file(argv[1], &bpe_size);
    uint8_t *fixed_data = read_file(argv[2], &fixed_size);
    BPE bpe;
    if (!parse_bpe(&bpe, bpe_data, bpe_size)) {
        fprintf(stderr, "invalid BPE1 file\n");
        return 2;
    }

    uint64_t bpe_checksum = decode_bpe_all(&bpe);
    uint64_t fixed_checksum = decode_fixed_all(fixed_data, bpe.weights, bpe.bits);
    if (bpe_checksum != fixed_checksum) {
        fprintf(
            stderr,
            "checksum mismatch bpe=%016" PRIx64 " fixed=%016" PRIx64 "\n",
            bpe_checksum,
            fixed_checksum
        );
        return 3;
    }

    double bpe_times[5];
    double fixed_times[5];
    volatile uint64_t warm_bpe = decode_bpe_all(&bpe);
    volatile uint64_t warm_fixed = decode_fixed_all(fixed_data, bpe.weights, bpe.bits);
    (void)warm_bpe;
    (void)warm_fixed;

    for (int pass = 0; pass < 5; pass++) {
        double started = now_seconds();
        volatile uint64_t decoded = decode_bpe_all(&bpe);
        bpe_times[pass] = now_seconds() - started;
        started = now_seconds();
        volatile uint64_t fixed = decode_fixed_all(fixed_data, bpe.weights, bpe.bits);
        fixed_times[pass] = now_seconds() - started;
        (void)decoded;
        (void)fixed;
    }
    qsort(bpe_times, 5, sizeof(double), compare_double);
    qsort(fixed_times, 5, sizeof(double), compare_double);

    const int samples = 10000;
    uint32_t *targets = malloc((size_t)samples * sizeof(uint32_t));
    uint64_t seed = 20260831ULL;
    for (int index = 0; index < samples; index++) {
        targets[index] = (uint32_t)(xorshift64(&seed) % bpe.blocks);
    }

    uint64_t *all_starts = malloc((size_t)bpe.blocks * sizeof(uint64_t));
    uint8_t *all_lengths = malloc((size_t)bpe.blocks);
    size_t position = bpe.data_start;
    uint64_t weight_start = 0;
    for (uint32_t block = 0; block < bpe.blocks; block++) {
        all_starts[block] = weight_start;
        int n = bpe.data[position] + 1;
        all_lengths[block] = (uint8_t)n;
        weight_start += (uint64_t)n;
        position += 2 + (size_t)bpe.data[position + 1];
    }

    uint64_t *starts = malloc((size_t)samples * sizeof(uint64_t));
    int *lengths = malloc((size_t)samples * sizeof(int));
    for (int index = 0; index < samples; index++) {
        starts[index] = all_starts[targets[index]];
        lengths[index] = all_lengths[targets[index]];
    }

    uint64_t random_bpe = FNV_OFFSET;
    uint64_t random_fixed = FNV_OFFSET;
    for (int index = 0; index < samples; index++) {
        random_bpe = decode_bpe_random(&bpe, targets[index], random_bpe);
        for (int offset = 0; offset < lengths[index]; offset++) {
            int value = sign_magnitude_decode(
                fixed_code_at(fixed_data, starts[index] + (uint64_t)offset, bpe.bits),
                bpe.bits
            );
            random_fixed = fnv_quantized(random_fixed, (int16_t)value);
        }
    }
    if (random_bpe != random_fixed) {
        fprintf(stderr, "random-access checksum mismatch\n");
        return 4;
    }

    double started = now_seconds();
    random_bpe = FNV_OFFSET;
    for (int index = 0; index < samples; index++) {
        random_bpe = decode_bpe_random(&bpe, targets[index], random_bpe);
    }
    double bpe_random_seconds = now_seconds() - started;

    started = now_seconds();
    random_fixed = FNV_OFFSET;
    for (int index = 0; index < samples; index++) {
        for (int offset = 0; offset < lengths[index]; offset++) {
            int value = sign_magnitude_decode(
                fixed_code_at(fixed_data, starts[index] + (uint64_t)offset, bpe.bits),
                bpe.bits
            );
            random_fixed = fnv_quantized(random_fixed, (int16_t)value);
        }
    }
    double fixed_random_seconds = now_seconds() - started;
    if (random_bpe != random_fixed) {
        fprintf(stderr, "timed random-access checksum mismatch\n");
        return 4;
    }

    double bpe_mweights = (double)bpe.weights / bpe_times[2] / 1e6;
    double fixed_mweights = (double)bpe.weights / fixed_times[2] / 1e6;

    printf("{\n");
    printf("  \"bits\": %u,\n", bpe.bits);
    printf("  \"weights\": %" PRIu64 ",\n", bpe.weights);
    printf("  \"blocks\": %u,\n", bpe.blocks);
    printf("  \"index_stride\": %u,\n", bpe.stride);
    printf("  \"bpe_bytes\": %zu,\n", bpe_size);
    printf("  \"fixed_bytes\": %zu,\n", fixed_size);
    printf("  \"bpe_bits_per_weight\": %.9f,\n", 8.0 * bpe_size / bpe.weights);
    printf("  \"fixed_bits_per_weight\": %.9f,\n", 8.0 * fixed_size / bpe.weights);
    printf("  \"size_ratio\": %.9f,\n", (double)bpe_size / fixed_size);
    printf("  \"bpe_decode_mweights_s\": %.6f,\n", bpe_mweights);
    printf("  \"fixed_decode_mweights_s\": %.6f,\n", fixed_mweights);
    printf("  \"decode_throughput_ratio\": %.9f,\n", bpe_mweights / fixed_mweights);
    printf("  \"bpe_random_us_per_block\": %.6f,\n", bpe_random_seconds * 1e6 / samples);
    printf("  \"fixed_random_us_per_block\": %.6f,\n", fixed_random_seconds * 1e6 / samples);
    printf("  \"random_latency_ratio\": %.9f,\n", bpe_random_seconds / fixed_random_seconds);
    printf("  \"checksum\": \"%016" PRIx64 "\",\n", fixed_checksum);
    printf("  \"random_checksum\": \"%016" PRIx64 "\"\n", random_bpe);
    printf("}\n");

    free(bpe_data);
    free(fixed_data);
    free(targets);
    free(all_starts);
    free(all_lengths);
    free(starts);
    free(lengths);
    return 0;
}
