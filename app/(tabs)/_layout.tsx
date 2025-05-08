import { View, Text, ImageBackground, Image } from 'react-native'
import React from 'react';
import { Tabs } from 'expo-router';
import { icons } from "@/constants/icons";
import { images } from "@/constants/images";

const _layout = () => {
  return (
    <Tabs>
        <Tabs.Screen
            name="index"
            options={{
                title: 'Home',
                headerShown: false,
                tabBarIcon: ({ focused }) => (
                    <>
                        <ImageBackground
                            source={images.highlight}
                            className="flex flex-row w-full flex-1 min-w-[112px] min-h-14 mt-4 justify-center items-center rounded-full overflow-hidden"
                        >
                            <Image source={icons.home}
                                tintColor="#151312" className='size-5' />
                        </ImageBackground>
                    </>
                ),
            }}
        />
        <Tabs.Screen   
            name="add"
            options={{
                title: 'Add',
                headerShown: false,
                tabBarIcon: ({ focused }) => (
                    <>
                        <ImageBackground
                            source={images.highlight}
                            className="flex flex-row w-full flex-1 min-w-[112px] min-h-14 mt-4 justify-center items-center rounded-full overflow-hidden"
                        >
                            <Image source={icons.add}
                                tintColor="#151312" className='size-5' />
                        </ImageBackground>
                    </>
                ),
            }}
        />
        <Tabs.Screen
            name="ranks"
            options={{
                title: 'Ranks',
                headerShown: false,
                tabBarIcon: ({ focused }) => (
                    <>
                        <ImageBackground
                            source={images.highlight}
                            className="flex flex-row w-full flex-1 min-w-[112px] min-h-14 mt-4 justify-center items-center rounded-full overflow-hidden"
                        >
                            <Image source={icons.medal}
                                tintColor="#151312" className='size-5' />
                        </ImageBackground>
                    </>
                ),
            }}
        />
        <Tabs.Screen
            name="stats"
            options={{
                title: 'Stats',
                headerShown: false,
                tabBarIcon: ({ focused }) => (
                    <>
                        <ImageBackground
                            source={images.highlight}
                            className="flex flex-row w-full flex-1 min-w-[112px] min-h-14 mt-4 justify-center items-center rounded-full overflow-hidden"
                        >
                            <Image source={icons.stats}
                                tintColor="#151312" className='size-5' />
                        </ImageBackground>
                    </>
                ),
            }}
        />
    </Tabs>
  )
}

export default _layout