import {Dropzone, MIME_TYPES} from '@mantine/dropzone';
import { IconUpload, IconPhoto, IconX } from '@tabler/icons-react';
import {Group, Text} from '@mantine/core';
import type {ImageMatchResult} from "../../models/ImageMatchResult.ts";


// TODO move this over into a service
async function uploadFile(file: File): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);
    try {
        const result = await fetch("http://localhost:8000/api/uploadfile", {
            method: 'POST',
            body: formData
        });
        const data = (await result.json()) as ImageMatchResult;
        console.log('Result: ', data)
    }
    catch (error) {
        console.error(error);
    }
}

const handleFileDrop = async (files: File[]) => {
    console.log('Dropzone dropped file: ', files[0].name);
    await uploadFile(files[0])
    console.log('File upload completed');
}

export default function ImageDropper() {
    return (
            <Dropzone.FullScreen
                className="dropcontaine"
                active={true}
                accept={[
                    MIME_TYPES.png,
                    MIME_TYPES.jpeg
                ]}
                maxSize={10 * 1024 ** 2}
                onDrop={handleFileDrop}
                onReject={() => { console.log('Dropzone rejected'); }}
            >
                <Group justify="center" gap="xl" mih={"80vh"} miw={"100vw"}>
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