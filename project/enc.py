#Jonathan,Fibush,207084336
#Python 3.8.1

from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES


# In the function we perform the decryption of CBC mode as studies in the lecture.
# Namely, each block (starting from the 2nd, since the 1st is the IV) is decrypted using AES,
# and the result is XORed with the previous cipher block to get the original plain text block.
def cbc_custom_decrypt(k, n, cipher):
    cipherObj = AES.new(k, AES.MODE_ECB)
    plainText = b''
    for i in range(1, n+1):
        # The bytes corresponding to the ith block
        decryptedBlock = cipherObj.decrypt(cipher[16*i: 16*(i+1)])
        # The bytes corresponding to the (i-1)th block
        plainTextBlock = xorBytes(decryptedBlock, cipher[16*(i-1): 16*i])
        plainText += plainTextBlock
    return plainText


# In the function we first find i - the index of the corrupted cipher block. Then, we restore the correct plain text of block i+1,
# knowing that only one bit got flipped and that each block consists of a byte repeated 16 times. Afterwards, we restore the correct cipher text of block i, and finally we restore the original plain text block i.
def cbc_flip_fix(k, n, cipher):
    plainText = cbc_custom_decrypt(k, n, cipher)
    corruptedIndex = -1
    # finding the index of the block whose decryption got completely corrupted. Blocks [0, n-2] in the plain text corresponds to blocks [1, n-1] in the cipher text (because of the IV),
    # and we are given that the block whose decryption got completely corrupted is in the range [1, n-1]
    for i in range(0, n-1):
        currBlock = plainText[16*i: 16*(i+1)]
        # if all the 16 bytes of the block are identical, skipping to the next iteration
        if all(byte == currBlock[0] for byte in currBlock):
            continue
        corruptedIndex = i+1  # adding 1 because of the IV in the cipher, since we're going to use this index relative to the indices of the blocks in the cipher text
        break
    cipherObj = AES.new(k, AES.MODE_ECB)
    # decrypting the block right after the corrupted one
    decryptedFlippedBlock = cipherObj.decrypt(
        cipher[16*(corruptedIndex+1): 16*(corruptedIndex+2)])
    # the plain text of that block, apart from a single flipped bit
    plainTextFlippedBlock = plainText[16 *
                                      corruptedIndex: 16*(corruptedIndex+1)]
    # retrieving the correct plain text of that block
    orgPlainTextFlippedBlock = retrieve_org_block(plainTextFlippedBlock)
    # finally restoring the correct cipher text block whose decryption got corrupted, and decrypting it.
    # The correctness stems from the fact that original cipher block i (i=corruptedIndex) XOR plain text block i+1 = decryptedFlippedBlock.
    # XORing both sides of the equation with plain text block i+1 yields the equality expressed in the statement
    # (original cipher block i=decryptedFlippedBlock XOR plain text block i+1)
    orgDecrtyptedBlock = cipherObj.decrypt(
        xorBytes(orgPlainTextFlippedBlock, decryptedFlippedBlock))
    # XORing the result with cipher block i-1 to restore the original block
    return xorBytes(orgDecrtyptedBlock, cipher[16*(corruptedIndex-1): 16*corruptedIndex])

# helper function for XORing 2 bytes object byte-byte


def xorBytes(bytes1, bytes2):
    return bytes(a ^ b for a, b in zip(bytes1, bytes2))

# helper function that given the plain text block with a single bit flipped, produces the correct block without a flipped bit.
# The correct block consists of a byte repeated 16 times, therefore in the received block only one byte among the 16 is different.


def retrieve_org_block(block):
    orgByte = block[0:1]
    # if the first 2 bytes aren't the same, then one of them is the different one, meaning that the 3rd byte is necessarily the original byte.
    # Otherwise, if the 2 first bytes are the same, both of them are the original byte.
    if block[0] is not block[1]:
        orgByte = block[2:3]
    return orgByte*16
