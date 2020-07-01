nums = [0x1, 0xA, 0x3, 0x2, 0x5, 0x9, 0x8, 0x7, 0x4, 0x6]

changed = True

while changed:
    changed = False
    for i in range(len(nums)-1):
        if nums[i] > nums[i+1]:
            print(f"swap {i}")
            nums[i] ^= nums[i+1]
            nums[i+1] ^= nums[i]
            nums[i] ^= nums[i+1]
            changed = True

print(nums)
