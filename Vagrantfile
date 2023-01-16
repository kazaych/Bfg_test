# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
    config.vm.box = "ubuntu/bionic64"
  
    config.vm.provision "ansible" do |ansible|
      ansible.verbose = "vvv"
      ansible.playbook = "provisioning/playbook.yml"
      ansible.become= "true"
    end
  
  
    config.vm.provider "virtualbox" do |v|
        v.check_guest_additions = false
        v.memory = 2048
        v.cpus = 2
    end
  
    config.vm.define "server" do |server|
      server.vm.network "private_network", ip: "192.168.56.10"
      server.vm.network "forwarded_port", guest: 80, host: 8088
      server.vm.hostname = "server"
    end
end