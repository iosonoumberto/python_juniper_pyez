#! /usr/bin/python

from employee import employee

def main():
    paul = employee('paul',23,30000)
    laura = employee('laura',21,40000)

    laura.get()
    paul.get()

    laura.birthday()
    laura.money(5000)
    paul.money(3000)

    laura.get()
    paul.get()

if __name__ == "__main__":
    main()

