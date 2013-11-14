import sys

sys.path.append('tools')
import addons_xml_generator
import zip_generator

def make_release():
  addons_xml_generator.Generator()
  zip_generator.main()

if __name__ == '__main__':
  make_release()
