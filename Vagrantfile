# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.define "etl" do |etl|
    etl.vm.box = "ubuntu/bionic64"
    config.vm.box = "ubuntu/trusty64"
    config.env.enable # Enable vagrant-env(.env)
    etl.vm.provision "shell", inline: "rm -rf ~/.bash_profile", privileged: false
    etl.vm.provision "shell", inline: "echo \'export ROOT_ENV_PATH=\"#{ENV['VENV_PATH']}\"\' >> ~/.bash_profile", privileged: false
    etl.vm.provision "shell", inline: "echo \'export PYTHON_ENV_PATH=\"#{ENV['PROJECT_PATH']}\"\' >> ~/.bash_profile", privileged: false
    etl.vm.provision "shell", inline: "source ~/.bash_profile", privileged: false
    # etl.vm.provision "shell", inline: "echo $ROOT_ENV_PATH", privileged: false
    # etl.vm.provision "shell", inline: "echo $PYTHON_ENV_PATH", privileged: false
    etl.vm.provision "shell", path: "setup/provision_etl.sh", env: {PROJECT_PATH:"teste", VENV_PATH:"123456"}
    etl.vm.provision "shell", inline: 'echo ". /home/vagrant/venv/bin/activate && cd /vagrant" > ~/.profile', privileged: false
    etl.vm.network "private_network", ip: "192.168.33.10"
  end

  config.vm.define "db" do |db|
    db.vm.box = "bigdeal/mysql57"
    db.vm.provision "shell", path: "setup/provision_db.sh"
    db.vm.network "private_network", ip: "192.168.33.11"
  end
end
