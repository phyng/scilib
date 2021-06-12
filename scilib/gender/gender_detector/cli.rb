
require 'gender_detector'

d = GenderDetector.new :case_sensitive => false
for arg in ARGV
  puts "#{arg},#{d.get_gender(arg)}"
end
