#include "flatbuffers/flatbuffers.h"
#include "flatbuffers/idl.h"
#include "flatbuffers/util.h"
#include "flatbuffers/flatbuffers.h"
#include "strawpoll_generated.h" // Already includes "flatbuffers/flatbuffers.h"

int main(int argc, char** argv) {

  const size_t data_len = 3;

  const uint8_t* data = new uint8_t[data_len]{1,2,3};

  const auto verifier = flatbuffers::Verifier(
    data,
    data_len
  );

  delete[] data;

  return 0;
}
