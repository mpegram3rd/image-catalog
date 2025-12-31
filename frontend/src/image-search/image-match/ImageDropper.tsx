import {Dropzone, MIME_TYPES} from '@mantine/dropzone';
import { IconUpload, IconPhoto, IconX } from '@tabler/icons-react';
import {Group, Text} from '@mantine/core';

export default function ImageDropper() {
    return (
            <Dropzone.FullScreen
                active={true}
                accept={[
                    MIME_TYPES.png,
                    MIME_TYPES.jpeg
                ]}
                onDrop={() => { console.log('Dropzone dropped'); }}
                onReject={() => { console.log('Dropzone rejected'); }}
            >
                <Group justify="center" gap="xl" mih={220} >
                    {/* children */}
                    <Dropzone.Accept>
                        <IconUpload size={52} color="var(--mantine-color-blue-6)" stroke={1.5} />
                    </Dropzone.Accept>
                    <Dropzone.Reject>
                        <IconX size={52} color="var(--mantine-color-red-6)" stroke={1.5} />
                    </Dropzone.Reject>
                    <Dropzone.Idle>
                        <IconPhoto size={52} color="var(--mantine-color-dimmed)" stroke={1.5} />
                    </Dropzone.Idle>
                    <div>
                        <Text size="xl" inline={true}>
                            Search for Similar Images
                        </Text>
                    </div>
                </Group>
            </Dropzone.FullScreen>
    );
}