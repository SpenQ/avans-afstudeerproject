from cffi import FFI
ffi = FFI()
ffi.cdef("""
    struct CpAbeCiphertext;
    struct CpAbeContext;
    struct CpAbeSecretKey;

    struct CpAbeContext* rabe_bsw_context_create();
    void rabe_bsw_context_destroy(struct CpAbeContext* ctx);
    struct CpAbeSecretKey* rabe_bsw_keygen(const struct CpAbeContext* ctx, const char* attributes);
    void rabe_bsw_keygen_destroy(void* sk);
    int32_t rabe_bsw_encrypt(const void* pk, char* policy, char* pt, int32_t pt_len, char** ct, int32_t *ct_len);
    int32_t rabe_bsw_decrypt(const struct CpAbeSecretKey* sk, const char* ct, uint32_t ct_len, char** pt_buf, uint32_t *pt_len);
""")

C = ffi.dlopen("/home/spenq/Source/rabe/target/debug/librabe.so")

ctx = C.rabe_bsw_context_create()
print(ctx)
sk = C.rabe_bsw_keygen(ctx, b"[ \"test1\", \"test2\", \"test3\" ]")
print(sk)
pt = b"testing123"

output = C.rabe_bsw_encrypt(ctx, b"{\"OR\": [{\"ATT\": \"A\"}, {\"ATT\": \"B\"}]}", pt, len(pt))
print(output)