/*
 * UserInformation.cpp
 *
 *  Created on: 4 dic 2019
 *      Author: giado
 */

#include "UserInformation.h"

UserInformation::UserInformation()
{
    CQI = omnetpp::intuniform(rng, 1, 16);
    FIFOQueue = new cQueue();
    remainingBytes = CQIToBytes();
    lastRB = 0;
}

int UserInformation::CQIToBytes()
{
    int bytes[] = {3, 3, 6, 11, 15, 20, 25, 36, 39, 50, 63, 72, 80, 93, 93};
    return bytes[CQI-1];
}

void UserInformation::generateCQI()
{
    CQI = omnetpp::intuniform(rng, 1, 16); // tbd: per il momento facciamo uniform e con magicnumbers
}


omnetpp::cQueue* UserInformation::getQueue()
{
    return FIFOQueue;
}


std::vector<Packet*> UserInformation::getPackets(int available)
{
    // IDEA: return as much packets as i can fit
    std::vector<Packet*> pkts;
    while(!FIFOQueue->empty())
    {
        Packet *p = FIFOQueue->head();
        if(available < ceil(p->getSize()/CQIToBytes(CQI))
        {
            pkts.push_back(FIFOQueue->pop());
            available -= 1;
        }
    }
    return pkts;
}

UserInformation::~UserInformation()
{
    // idk if this is ok (i kinda forgot most of the shit about c++)
    delete this->FIFOQueue;
}
