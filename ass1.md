**CSE/PC/B/S/314   Computer Networks Lab**

CO1: Design and implement error detection techniques within a simulated network environment.

**Assignment 1:**  Design and implement an error detection module which has two schemes namely Checksum and Cyclic Redundancy Check(CRC). 

**Code demonstration due on:*** 18-22 August 2025 (in your respective lab classes)  **Report submission due on:** 25-29 August 2025 (in respective lab classes) Softcopy of the report to be uploaded in the drive. 

**Language:** You can write the program in any high level language like C, C++, Java, Python etc. 

Please note that you may need to use these schemes separately for other applications (assignments).  

**Sender Program:** The Sender program should accept the name of a test file (contains a sequence of 0,1) from  the  command  line.  Then  it  will  prepare  the  dataword  from  the  input. Based on the schemes, codewords will be prepared. Sender will send the codewords to the Receiver.  

**Error  injection  module:**  Inject  error  in  random  positions  in  the  input  data  frame.  Write  a  separate method for that. Sender program will randomly call this method before sending the codewords to the receiver.**  

**Receiver Program:** Receiver will check if there is any error detected. Based on the detection it will accept or reject the dataword. 

- **Checksum (16-bit):** Checksum of a block of data is the complement of the one's complement of the 16-bit sum of the block. The message (from the input file) is divided into 16-bit words. The value of the checksum word is set to 0. All words are added using 1’s complement addition. The sum is complemented and becomes the checksum. So, if we transmit the block of data including the checksum field, the receiver should see a checksum of 0 if there are no bit errors. 
- **CRC:**  CRC  generator  polynomials  will  be  given  as input (CRC-8, CRC-10, CRC-16 and CRC-32). Show  how  good  is  the  selected  polynomial  to  detect  single-bit  error,  two isolated single-bit errors, odd number of errors, and burst errors.  
  - CRC-8: x8 + x7 + x6 + x4 + x2 + 1  (Use: General,  Bluetooth wireless communication) 
  - CRC-10: x10 + x9 + x5 + x4 + x + 1 (Use: General, Telecommunication) 
  - CRC-16: x 16 + x15 + x2 + 1 (Use: USB) 
  - CRC-32: x32 + x26 + x23 + x22 + x16 + x12 + x11 + x10 + x8 + x7 + x5 + x4 + x2 + x + 1 (Use: Ethernet IEEE802.3) 
- **Error  types:**  single-bit  error,  two  isolated  single-bit  errors,  odd  number  of  errors,  and  burst errors. 

Test the above two schemes for the error types and CRC polynomials mentioned above for the  following cases (not limited to). 

- Error is detected by both CRC and Checksum.  
- Error is detected by checksum but not by CRC.  
- Error is detected by CRC but not by Checksum. 

**Note: Follow the instructions given for report preparation.** 
