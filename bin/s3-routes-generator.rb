#!/usr/bin/env ruby

require 'nokogiri'

routes = []

src = File.read(ARGV[0])

src.each_line do |line|
  from, to = line.split(/\s+/)

  from.gsub!(/\A\//, '')
  to.gsub!(/\/\z/, '/index.html')
  to.gsub!(/\A\//, '')

  routes << { :from => from, :to => to }
end

builder = Nokogiri::XML::Builder.new do |xml|
  xml.RoutingRules {
    routes.each do |route|
      xml.RoutingRule {
        xml.Condition {
          xml.KeyPrefixEquals route[:from]
        }

        xml.Redirect {
          xml.ReplaceKeyWith route[:to]
        }
      }
    end
  }
end

puts builder.to_xml
