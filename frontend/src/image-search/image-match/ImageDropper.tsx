import {Dropzone, MIME_TYPES} from '@mantine/dropzone';
import { IconUpload, IconPhoto, IconX } from '@tabler/icons-react';
import {Group, Text} from '@mantine/core';
import './ImageDropper.css'

export default function ImageDropper() {
    return (
        <Group justify="center" gap="xl" className="dropcontainer" >
            <Dropzone
                className="dropcontainer"
                accept={[
                    MIME_TYPES.png,
                    MIME_TYPES.jpeg
                ]}
                onDrop={() => { console.log('Dropzone dropped'); }}
                onReject={() => { console.log('Dropzone rejected'); }}
            >
                {/* children */}
                <Dropzone.Accept>
                    <IconUpload size={32} color="var(--mantine-color-blue-6)" stroke={1.5} />
                </Dropzone.Accept>
                <Dropzone.Reject>
                    <IconX size={32} color="var(--mantine-color-red-6)" stroke={1.5} />
                </Dropzone.Reject>
                <Dropzone.Idle>
                    <IconPhoto size={32} color="var(--mantine-color-dimmed)" stroke={1.5} />
                </Dropzone.Idle>
                    <Text size="xl" inline={true}>
                        Drop Images Here
                    </Text>
            </Dropzone>
       </Group>
    );
}